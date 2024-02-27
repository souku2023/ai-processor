from datetime import datetime
import logging
import os.path
import inspect
from concurrent.futures import ThreadPoolExecutor

class AppLogger:
    """
    """
    colorama_imported = None
    formatter_type = "DT_LOGLVL_MSG"

    class FormatterType:
        LOGLVL_MSG = "LOGLVL_MSG"
        DT_LOGLVL_MSG = "DT_LOGLVL_MSG"
        DT_LOGLVL_APP_MSG = "DT_LOGLVL_APP_MSG"
        LOGLVL_MODULE_MSG = "LOG_LVL_MODULE_MSG"
    
    class Type:
        INFO = 'INFO'
        WARN = 'WARNING'
        DEBUG = 'DEBUG'
        CRITICAL = 'CRITICAL'

    class Colors:
        DEBUG = '\033[0;35m'           # Purple
        INFO1 = '\033[94m'
        INFO = '\033[96m'
        # INFO = '\033[0;32m'            # Green
        WARN = '\033[0;33m'            # Orange
        CRTICAL = '\033[0;31m'         # Red
        ENDC = '\033[0m'               
        BOLD = '\033[1m'
        UNDERLINE = '\033[4m'


    is_logging = False
    is_logfile_enabled = True
    logfile_name = None
    logfile_base_name = None
    main_logger = None
    dupl_logger = None
    no_logger = None
    log_date_time = None
    executor = ThreadPoolExecutor()

    @staticmethod
    def log_str(error: Exception):
        """
        Returns a string containing the error
        """

        return f"{error.__class__.__qualname__}: {error} (in line {error.__traceback__.tb_lineno} of file {error.__traceback__.tb_frame.f_code.co_filename})"

    
    @staticmethod
    def setup_logger(logger_name, logNumLevel, log_file): # level=logging.INFO):
        try:
            l = logging.getLogger(logger_name)
            if AppLogger.formatter_type == AppLogger.FormatterType.DT_LOGLVL_APP_MSG:
                formatter = logging.Formatter(
                    fmt='%(asctime)s.%(msecs)03d,%(name)-12s,%(levelname)-8s,%(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
            elif AppLogger.formatter_type == AppLogger.FormatterType.LOGLVL_MSG:
                formatter = logging.Formatter(fmt='%(levelname)-8s, %(message)s')
            elif AppLogger.formatter_type == AppLogger.FormatterType.DT_LOGLVL_MSG:
                formatter = logging.Formatter(
                    fmt='%(asctime)s.%(msecs)03d,%(levelname)-8s, %(message)s')
            else:
                formatter = logging.Formatter(fmt='%(levelname)-8s, %(message)s')
            file_handler = logging.FileHandler(log_file, mode='w')
            file_handler.setFormatter(formatter)

            l.setLevel(logNumLevel)
            l.addHandler(file_handler)
        except Exception as e:
            print(f'LOG, Logger setup failed with : {AppLogger.log_str(error=e)}')

    @staticmethod
    def rename_log_file(old_name, new_name):
        if AppLogger.main_logger is not None:
            if len(AppLogger.main_logger.handlers)>0:
                try:
                    handler = None
                    for h in AppLogger.main_logger.handlers:
                        if h.__class__.__name__ == 'FileHandler':
                            handler = h
                    AppLogger.main_logger.removeHandler(handler)
                    handler.close()

                    # Rename the logfile on disk
                    os.rename(old_name, new_name)

            # New handler using new filename.  Note the 'append' flag
                    if AppLogger.formatter_type == AppLogger.FormatterType.DT_LOGLVL_APP_MSG:
                        formatter = logging.Formatter(
                            fmt='%(asctime)s.%(msecs)03d,%(name)-12s,%(levelname)-8s,%(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S')
                    elif AppLogger.formatter_type == AppLogger.FormatterType.LOGLVL_MSG:
                        formatter = logging.Formatter(fmt='%(levelname)-8s, %(message)s')
                    new_handler = logging.FileHandler(new_name, mode='a')
                    new_handler.setFormatter(formatter)
                    AppLogger.main_logger.addHandler(new_handler)
                except Exception as e:
                    print(f'LOG, Log renaming failed with : {AppLogger.log_str(error=e)}')

    @staticmethod
    def log(type):
        try:
            if not AppLogger.is_logging:
                AppLogger.is_logging = True
                logNumericLevel = getattr(logging, type.upper(), None)
                if AppLogger.is_logfile_enabled:
                    if AppLogger.logfile_base_name is None:
                        current_time = datetime.utcnow()
                        AppLogger.log_date_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
                        AppLogger.logfile_base_name = AppLogger.__get_logfile_name()
                        AppLogger.logfile_name = AppLogger.logfile_base_name
                        AppLogger.setup_logger('Nova', logNumericLevel, AppLogger.logfile_base_name)
                        AppLogger.main_logger = logging.getLogger('Nova')
                else:
                    logging.basicConfig(
                        level=logNumericLevel,
                        format='%(asctime)s.%(msecs)03d,%(name)-12s,%(levelname)-8s,%(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
                    AppLogger.no_logger = logging.getLogger()
                if not isinstance(logNumericLevel, int):
                    raise ValueError('Invalid log level: %s' % type)
        except Exception as e:
            print(f'LOG, AppLogger.log failed with : {AppLogger.log_str(error=e)}')


    @staticmethod
    def info(string: str):
        try:
            AppLogger.executor.submit(AppLogger.__info_thread, 
                                      string,
                                      inspect.stack()[1], 
                                      inspect.stack()[2])
            
        except IndexError:
            AppLogger.executor.submit(AppLogger.__info_thread, 
                                      string,
                                      inspect.stack()[1], 
                                      inspect.stack()[1])
        except Exception as e:
            print(f"{AppLogger.Colors.INFO}[CRITICAL]",
                  AppLogger.log_str(error=e))
    
        
    @staticmethod
    def warn(string: str):
        try:
            AppLogger.executor.submit(AppLogger.__warn_thread, 
                                      string,
                                      inspect.stack()[1], 
                                      inspect.stack()[2])
            
        except IndexError:
            # print(f"{AppLogger.Colors.INFO}[CRITICAL]", "IndexError")
            AppLogger.executor.submit(AppLogger.__warn_thread, 
                                      string,
                                      inspect.stack()[1], 
                                      inspect.stack()[1])
        except Exception as e:
            print(f"{AppLogger.Colors.INFO}[CRITICAL]",
                  AppLogger.log_str(error=e))
    
        
    @staticmethod
    def critical(string: str):
        try:
            AppLogger.executor.submit(AppLogger.__critical_thread, 
                                      string,
                                      inspect.stack()[1], 
                                      inspect.stack()[2])
            
        except IndexError:
            # print(f"{AppLogger.Colors.INFO}[CRITICAL]", "IndexError")
            AppLogger.executor.submit(AppLogger.__critical_thread, 
                                      string,
                                      inspect.stack()[1], 
                                      inspect.stack()[1])
        except Exception as e:
            print(f"{AppLogger.Colors.INFO}[CRITICAL]",
                  AppLogger.log_str(error=e))
        

    @staticmethod
    def debug(string: str):
        try:
            AppLogger.executor.submit(AppLogger.__debug_thread, 
                                      string,
                                      inspect.stack()[1], 
                                      inspect.stack()[2])
            
        except IndexError:
            # print(f"{AppLogger.Colors.INFO}[CRITICAL]", "IndexError")
            AppLogger.executor.submit(AppLogger.__debug_thread, 
                                      string,
                                      inspect.stack()[1], 
                                      inspect.stack()[1])
        except Exception as e:
            print(f"{AppLogger.Colors.INFO}[CRITICAL]",
                  AppLogger.log_str(error=e))
    

    @staticmethod
    def deinit_():
        """
        """
        AppLogger.executor.shutdown()

        

    @staticmethod
    def __info_thread(string, frame, previous_frame):
        print(f"[{AppLogger.Type.INFO : <8}] {string}", flush=True)

        # print(f"{Fore.GREEN}[{AppLogger.Type.INFO : <8}] {string}", flush=True)
        # Previous Frame
        # previous_frame = inspect.stack()[2]
        previous_file_ = previous_frame[1]
        previous_line_ = previous_frame[2]
        previous_method_ = previous_frame[3]
        previous_class_ = list(previous_frame[0].f_globals.keys())[-1]
        if previous_class_ == previous_method_:
            previous_str = f"{previous_method_} in line {previous_line_} of {previous_file_}"
        else:
            previous_str = f"{previous_class_}.{previous_method_} in line {previous_line_} of {previous_file_}."

        # Frame
        # frame = inspect.stack()[1]
        file_ = frame[1]
        line_ = frame[2]
        method_ = frame[3]
        class_ = list(frame[0].f_globals.keys())[-1]
        if class_ == method_:
            last_str =  f"{method_} in line {line_} of {file_}"
        else:
            last_str  = f"{class_}.{method_} in line {line_} of {file_}"

        str  = f"{string : <200}, {last_str} , called by {previous_str}".strip('\n').strip('\r')

        try:
            AppLogger.log(AppLogger.Type.INFO)
            if AppLogger.is_logfile_enabled:
                AppLogger.main_logger.info(str)
            else:
                AppLogger.no_logger.info(str)
        except Exception as e:
            print(f'LOG, AppLogger.info failed with : {AppLogger.log_str(error=e)} ::', str)

    @staticmethod
    def __warn_thread(string, frame, previous_frame):

        print(f"[{AppLogger.Type.WARN : <8}] {string}", flush=True)# print(f"[{AppLogger.Type.WARN : <8}]", string, flush=True)
        
        # Previous Frame
        previous_file_ = previous_frame[1]
        previous_line_ = previous_frame[2]
        previous_method_ = previous_frame[3]
        previous_class_ = list(previous_frame[0].f_globals.keys())[-1]
        if previous_class_ == previous_method_:
            previous_str = f"{previous_method_} in line {previous_line_} of {previous_file_}"
        else:
            previous_str = f"{previous_class_}.{previous_method_} in line {previous_line_} of {previous_file_}."

        # Frame
        file_ = frame[1]
        line_ = frame[2]
        method_ = frame[3]
        class_ = list(frame[0].f_globals.keys())[-1]
        if class_ == method_:
            last_str = f"{method_} in line {line_} of {file_}"
        else:
            last_str = f"{class_}.{method_} in line {line_} of {file_}"

        str  = f"{string : <200}, {last_str} , called by {previous_str}".strip('\n').strip('\r')

        try:
            AppLogger.log(AppLogger.Type.WARN)
            if AppLogger.is_logfile_enabled:
                AppLogger.main_logger.warn(str)
            else:
                AppLogger.no_logger.warn(str)
        except Exception as e:
            print(f'LOG, AppLogger.warn failed with : {AppLogger.log_str(error=e)}')

    @staticmethod
    def __critical_thread(string, frame, previous_frame):
        # print(f"[{AppLogger.Type.CRITICAL : <8}]", string, flush=True)

        print(f"[{AppLogger.Type.CRITICAL : <8}] {string}", flush=True)
    
        # Previous Frame
        previous_file_ = previous_frame[1]
        previous_line_ = previous_frame[2]
        previous_method_ = previous_frame[3]
        previous_class_ = list(previous_frame[0].f_globals.keys())[-1]
        if previous_class_ == previous_method_:
            previous_str = f"{previous_method_} in line {previous_line_} of {previous_file_}"
        else:
            previous_str = f"{previous_class_}.{previous_method_} in line {previous_line_} of {previous_file_}."

        # Frame
        file_ = frame[1]
        line_ = frame[2]
        method_ = frame[3]
        class_ = list(frame[0].f_globals.keys())[-1]
        if class_ == method_:
            last_str = f"{method_} in line {line_} of {file_}"
        else:
            last_str = f"{class_}.{method_} in line {line_} of {file_}"

        str  = f"{string : <200}, {last_str} , called by {previous_str}".strip('\n').strip('\r')
        
        try:
            AppLogger.log(AppLogger.Type.CRITICAL)
            if AppLogger.is_logfile_enabled:
                AppLogger.main_logger.critical(str)
            else :
                AppLogger.no_logger.critical(str)
        except Exception as e:
            print(f'LOG, AppLogger.critical failed with : {AppLogger.log_str(error=e)}')

    @staticmethod
    def __debug_thread(string, frame, previous_frame):
        
        print(f"[{AppLogger.Type.DEBUG : <8}] {string}", flush=True)
        # Previous Frame
        previous_file_ = previous_frame[1]
        previous_line_ = previous_frame[2]
        previous_method_ = previous_frame[3]
        previous_class_ = list(previous_frame[0].f_globals.keys())[-1]
        if previous_class_ == previous_method_:
            previous_str = f"{previous_method_} in line {previous_line_} of {previous_file_}"
        else:
            previous_str = f"{previous_class_}.{previous_method_} in line {previous_line_} of {previous_file_}."

        # Frame
        file_ = frame[1]
        line_ = frame[2]
        method_ = frame[3]
        class_ = list(frame[0].f_globals.keys())[-1]
        if class_ == method_:
            last_str = f"{method_} in line {line_} of {file_}"
        else:
            last_str = f"{class_}.{method_} in line {line_} of {file_}"

        str  = f"{string}, {last_str} , called by {previous_str}".strip('\n').strip('\r')
        str  = f"{string : <200}, {last_str} , called by {previous_str}".strip('\n').strip('\r')
        
        try:
            AppLogger.log(AppLogger.Type.DEBUG)
            if AppLogger.is_logfile_enabled:
                AppLogger.main_logger.debug(str)
                # AppLogger.dupl_logger.debug(str)
            else :
                AppLogger.no_logger.debug(str)
        except Exception as e:
            print(f'LOG, AppLogger.debug failed with : {AppLogger.log_str(error=e)}')

    @staticmethod
    def __get_logfile_name():
        try:
            if not os.path.exists('logs'):
                os.makedirs('logs')

            return 'logs//' + 'Nova_log_{}_{}_{}_{}_{}.log'.format(
                str(datetime.now().year),
                str(datetime.now().month), 
                str(datetime.now().day),
                str(datetime.now().hour),
                str(datetime.now().minute)
                )
        except Exception as e:
            print(f'LOG, AppLogger.get_file_name failed with : {AppLogger.log_str(error=e)}')

    @staticmethod
    def rename(filename):
        try:
            if AppLogger.logfile_name is not None:
                AppLogger.rename_log_file(AppLogger.logfile_name, AppLogger.logfile_base_name + '_'+ filename)
                AppLogger.info('GA_LOGGING, Log file renamed from %s to %s'%(AppLogger.logfile_name,AppLogger.logfile_base_name + '_'+ filename))
                AppLogger.logfile_name = AppLogger.logfile_base_name + '_'+ filename
        except Exception as e:
            print(f'LOG, AppLogger.rename failed with : {AppLogger.log_str(error=e)}')
