"""Scripts / Functions to setup a Logger"""
####################################################################################################
#                                      Scripts / Functions to setup a Logger                       #
#                                      Author:   XGWSLIT                                           #
#                                      Version:  1.0                                               #
#                                      Date:     2022-06-16                                        #
####################################################################################################

####################################################################################################
#                                           Imports                                                #
####################################################################################################
import datetime
import logging
import os


####################################################################################################
#                                          Functions                                               #
####################################################################################################
def setup_logger(
                name: str,
                level: int = 10,
                logging_directory: str = "log/",
                file_handler: bool = True,
                stream_handler: bool = True
                ) -> logging.Logger:
    """
    Create a Logger\n
    Log-Level:\n
     - CRITICAL(50)\n
     - ERROR(40)\n
     - WARNING(30)\n
     - INFO(20)\n
     - DEBUG(10)\n
     - NOTSET(0)\n
    -> DEFAULT = DEBUG (10)
    """
    # Create Logger
    logger = logging.getLogger()

    # Set Level
    logger.setLevel(level=level)

    # Setting Logging Entry format
    formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(message)s')

    # Check if the logging_directory exsists, if not it will be created
    if not os.path.exists(logging_directory):
        os.mkdir(logging_directory)

    # Setup file_handler:
    if file_handler:
        date = datetime.date.today()
        file_hander = logging.FileHandler(f'{logging_directory}/log_{date.strftime("%Y-%m-%d")}.log')
        file_hander.setFormatter(formatter)
        logger.addHandler(file_hander)

    # Setup stream_handler:
    if stream_handler:
        stream_hander = logging.StreamHandler()
        stream_hander.setFormatter(formatter)
        logger.addHandler(stream_hander)

    return logger


####################################################################################################
#                                            Setup                                                 #
####################################################################################################


####################################################################################################
#                                            Script                                                #
####################################################################################################