import io
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from types import ModuleType
import unittest
from unittest.mock import Mock, call, patch

import main


class MainTests(unittest.TestCase):
    def setUp(self):
        self.directory = TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.config_directory = Path(self.directory.name)
        self.enterContext(patch.object(main, "CONFIG_DIRECTORY", self.config_directory))
        self.enterContext(patch.object(main, "setup_logging"))
        self.enterContext(patch.object(main, "log"))

    def test_execute_all_filters_sorts_and_runs_each_config_before_loading_next(self):
        for filename in ("z.py", "B.py", "a.py", "config.py", "__init__.py",
                         "logging.json", "config.py.bak"):
            (self.config_directory / filename).touch()
        (self.config_directory / "directory.py").mkdir()
        (self.config_directory / "examples").mkdir()
        (self.config_directory / "examples" / "nested.py").touch()
        events = Mock()
        with patch.object(main, "load_config", side_effect=lambda name: name) as load:
            with patch.object(main, "run_config", return_value=True) as run:
                events.attach_mock(load, "load")
                events.attach_mock(run, "run")
                self.assertEqual(main.main(["--execute-all"]), 0)
        self.assertEqual(events.mock_calls, [
            call.load("a.py"), call.run("a.py"),
            call.load("B.py"), call.run("B.py"),
            call.load("config.py"), call.run("config.py"),
            call.load("z.py"), call.run("z.py"),
        ])

    def test_config_error_does_not_prevent_later_config(self):
        for filename in ("a.py", "b.py"):
            (self.config_directory / filename).touch()
        with patch.object(main, "load_config", side_effect=[SyntaxError("bad config"), {}]):
            with patch.object(main, "run_config", return_value=True) as run:
                self.assertEqual(main.main(["--execute-all"]), 1)
        run.assert_called_once_with({})

    def test_default_and_explicit_config(self):
        for arguments, filename in (([], "config.py"), (["production"], "production"),
                                    (["production.py"], "production.py")):
            with self.subTest(arguments=arguments):
                with patch.object(main, "load_config", return_value={}) as load:
                    with patch.object(main, "run_config", return_value=True):
                        self.assertEqual(main.main(arguments), 0)
                load.assert_called_once_with(filename)

    def test_empty_selection_fails(self):
        self.assertEqual(main.main(["--execute-all"]), 1)

    def test_conflicting_arguments_fail_before_setup(self):
        with patch("sys.stderr", new_callable=io.StringIO):
            with self.assertRaises(SystemExit) as error:
                main.main(["config.py", "--execute-all"])
        self.assertEqual(error.exception.code, 2)
        main.setup_logging.assert_not_called()

    def test_help_does_not_initialize_logging_or_load_configs(self):
        with patch.object(main, "load_config") as load:
            with patch("sys.stdout", new_callable=io.StringIO) as output:
                with self.assertRaises(SystemExit) as error:
                    main.main(["--help"])
        self.assertEqual(error.exception.code, 0)
        self.assertIn("--execute-all", output.getvalue())
        main.setup_logging.assert_not_called()
        load.assert_not_called()

    def test_real_config_loading_continues_after_config_errors(self):
        failures = (
            "config = {",
            "raise ImportError('broken dependency')",
            "other_variable = {}",
            "config = []",
        )
        for source in failures:
            with self.subTest(source=source):
                (self.config_directory / "a.py").write_text(source, encoding="utf-8")
                (self.config_directory / "b.py").write_text("config = {}", encoding="utf-8")
                with patch.object(main, "run_config", wraps=main.run_config) as run:
                    self.assertEqual(main.main(["--execute-all"]), 1)
                self.assertEqual(run.call_args_list[-1], call({}))
                self.assertTrue(callable(main.load_config))

    def test_failed_config_does_not_prevent_later_config(self):
        for filename in ("a.py", "b.py"):
            (self.config_directory / filename).touch()
        for first_result in (False, RuntimeError("process failed")):
            with self.subTest(first_result=first_result):
                with patch.object(main, "load_config", return_value={}):
                    with patch.object(main, "run_config", side_effect=[first_result, True]) as run:
                        self.assertEqual(main.main(["--execute-all"]), 1)
                self.assertEqual(run.call_count, 2)

    def test_real_config_loader_supports_filename_without_extension(self):
        (self.config_directory / "production.py").write_text(
            "config = {'ETL': {'processes': []}}", encoding="utf-8"
        )
        self.assertEqual(main.load_config("production"), {"ETL": {"processes": []}})
        self.assertEqual(main.main(["production"]), 0)

    def test_config_loader_rejects_paths_outside_config_directory(self):
        for filename in ("../outside.py", "examples/nested.py"):
            with self.subTest(filename=filename):
                with self.assertRaises(ValueError):
                    main.load_config(filename)

    def test_missing_single_config_reports_argument_error(self):
        with patch("sys.stderr", new_callable=io.StringIO):
            with self.assertRaises(SystemExit) as error:
                main.main(["missing.py"])
        self.assertEqual(error.exception.code, 2)

    def test_setup_failure_does_not_start_etl(self):
        main.setup_logging.side_effect = RuntimeError("logging failed")
        with patch.object(main, "load_config") as load:
            self.assertEqual(main.main([]), 1)
        load.assert_not_called()


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.enterContext(patch.object(main, "log"))
        self.data = {"items": [{"value": 1}]}
        self.extractor = Mock()
        self.extractor.setup.return_value = True
        self.extractor.extract.return_value = self.data
        self.transformer = Mock()
        self.transformer.setup.return_value = True
        self.transformer.transform.return_value = self.data
        self.loader = Mock()
        self.loader.setup.return_value = True
        self.loader.load.return_value = True
        self.extract_factory = Mock()
        self.extract_factory.create_extractor.return_value = self.extractor
        self.transform_factory = Mock()
        self.transform_factory.create_transformer.return_value = self.transformer
        self.load_factory = Mock()
        self.load_factory.create_loader.return_value = self.loader
        modules = {}
        for name, factory in (
            ("ETLExtract", self.extract_factory),
            ("ETLTransform", self.transform_factory),
            ("ETLLoad", self.load_factory),
        ):
            module_name = f"scripts.classes.{name}"
            module = ModuleType(module_name)
            setattr(module, f"{name}Factory", factory)
            modules[module_name] = module
        self.enterContext(patch.dict(sys.modules, modules))
        self.process = {
            "name": "first", "active": True,
            "extraction": {"type": "mock"},
            "transformation": {"type": "mock"},
            "loading": {"type": "mock"},
        }

    def test_successful_pipeline_and_loading_function_remains_callable(self):
        load_config = main.load_config
        self.assertTrue(main.run_config({"ETL": {"processes": [self.process]}}))
        self.transformer.transform.assert_called_once_with(self.data)
        self.loader.load.assert_called_once_with(self.data)
        self.assertIs(main.load_config, load_config)

    def test_inactive_process_is_skipped(self):
        self.process["active"] = False
        self.assertTrue(main.run_config({"ETL": {"processes": [self.process]}}))
        self.extract_factory.create_extractor.assert_not_called()

    def test_transformation_is_optional(self):
        self.process.pop("transformation")
        self.assertTrue(main.run_config({"ETL": {"processes": [self.process]}}))
        self.transform_factory.create_transformer.assert_not_called()
        self.loader.load.assert_called_once_with(self.data)

    def test_stage_failures_skip_later_stages_but_continue_with_next_process(self):
        failure = RuntimeError("stage failed")
        cases = (
            ("extract factory", self.extract_factory.create_extractor, [failure, self.extractor], 1, 1),
            ("extract setup false", self.extractor.setup, [False, True], 1, 1),
            ("extract setup exception", self.extractor.setup, [failure, True], 1, 1),
            ("extract exception", self.extractor.extract, [failure, self.data], 1, 1),
            ("extract missing data", self.extractor.extract, [None, self.data], 1, 1),
            ("transform factory", self.transform_factory.create_transformer,
             [failure, self.transformer], 1, 1),
            ("transform setup false", self.transformer.setup, [False, True], 1, 1),
            ("transform setup exception", self.transformer.setup, [failure, True], 1, 1),
            ("transform exception", self.transformer.transform, [failure, self.data], 2, 1),
            ("transform missing data", self.transformer.transform, [None, self.data], 2, 1),
            ("load factory", self.load_factory.create_loader, [failure, self.loader], 2, 1),
            ("load setup false", self.loader.setup, [False, True], 2, 1),
            ("load setup exception", self.loader.setup, [failure, True], 2, 1),
            ("load exception", self.loader.load, [failure, True], 2, 2),
            ("load false", self.loader.load, [False, True], 2, 2),
        )
        for name, method, results, transform_calls, load_calls in cases:
            with self.subTest(stage=name):
                for mock in (self.extract_factory, self.transform_factory, self.load_factory,
                             self.extractor, self.transformer, self.loader):
                    mock.reset_mock()
                processes = [self.process, dict(self.process, name="second")]
                method.side_effect = results
                try:
                    self.assertFalse(main.run_config({"ETL": {"processes": processes}}))
                finally:
                    method.side_effect = None
                self.assertEqual(self.transformer.transform.call_count, transform_calls)
                self.assertEqual(self.loader.load.call_count, load_calls)
                self.assertEqual(self.loader.load.call_args, call(self.data))


if __name__ == "__main__":
    unittest.main()