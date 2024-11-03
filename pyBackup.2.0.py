#!/usr/bin/env python3

import subprocess, logging, time
from logging.handlers import RotatingFileHandler

# Define the home directory
HOME_DIR = "/home/siskourso/"

# Define backup locations (source: destination)
BACKUP_LOCATIONS = {
    "/home/siskourso/Downloads/": "gdrive:/Backups/-Orion-/Downloads/",
    "/home/siskourso/Working/": "gdrive:/Backups/-Orion-/Working/",
    HOME_DIR: "gdrive:/Backups/-Orion-/Home/",
}

# Define main rclone arguments
ARGS = [
    "--transfers=10", 
    "--progress",
    "--verbose",
    "--exclude=*/*.log",
    "--drive-chunk-size=64M",
]

# Define rclone arguments for home directory in addition to main arguments
HOME_ARGS = [
    "--exclude=.*/",
    "--exclude=.*",
    "--exclude=*/*.log",
    "--exclude=Downloads/",
    "--exclude=Working/",
    "--exclude=Templates/",
    "--exclude=Public/",
    "--exclude=go/",
    "--exclude=Desktop/",
    "--exclude=gPodder/",
    "--exclude=snap/",
    "--exclude=Documents/test.pcapng"
]

# Define logging settings
CONSOLE_OUTPUT = True  # Set to True/False to toggle console logging
LOG_LEVEL = logging.DEBUG  # Change Logging levels to INFO, DEBUG, WARNING, ERROR
LOG_FILE = "pyBackup.log"  # Set the path/name to the log file
LOG_SIZE = 104857600  # Set the maximum log file size in bytes default is 100MB
LOG_BACKUPS = 5  # Set the maximum number of log files to keep

def setup_logging(log_file=LOG_FILE, max_bytes=LOG_SIZE, backup_count=LOG_BACKUPS, log_level=LOG_LEVEL):
    """
    Sets up the logging configuration for the application.

    Configures a rotating file handler and a console stream handler to log messages.
    The log messages include timestamps, log levels, and the message itself.

    Args:
        log_file (str): The path to the log file.
        max_bytes (int): The maximum size of the log file in bytes before it is rotated.
        backup_count (int): The number of backup log files to keep.
        log_level (int): The logging level (e.g., logging.DEBUG, logging.INFO).

    Returns:
        tuple: A tuple containing the logger and the console logging handler.
    """
    log_handler = RotatingFileHandler(log_file, maxBytes=max_bytes, backupCount=backup_count, delay=True)
    console_logging = logging.StreamHandler()
    
    log_handler.setLevel(log_level)
    console_logging.setLevel(log_level)
    
    log_formatting = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    log_handler.setFormatter(log_formatting)
    console_logging.setFormatter(log_formatting)
    
    logger = logging.getLogger("rclone_backup")
    logger.setLevel(log_level)
    logger.addHandler(log_handler)
    logger.addHandler(console_logging)
    
    return logger, console_logging

logger, console_logging = setup_logging()

def console_output(enabled):
    """
    Enables or disables console logging based on the value of the enabled parameter.

    If enabled is True, a logging.StreamHandler is added to the logger, and the message "Console logging enabled" is logged at the INFO level.
    If enabled is False, the logging.StreamHandler is removed from the logger, and the message "Console logging disabled" is logged at the INFO level.

    Args:
        enabled (bool): A boolean indicating whether to enable or disable console logging.
    """
    if enabled:
        logger.addHandler(console_logging)
        logger.info("Console logging enabled")
    else:
        logger.removeHandler(console_logging)
        logger.info("Console logging disabled")

def rclone_sync(source, destination, args=None):
    """
    Synchronizes the contents of the source directory with the destination directory using rclone.
    
    Args:
        source (str): The source directory path.
        destination (str): The destination directory path.
        args (list, optional): Optional list of additional arguments or flags for the rclone command.
    
    Logs the rclone command being executed. If the command executes successfully, logs a completion message and the 
    standard output and error. If an error occurs during execution, logs the error details including standard output 
    and error.
    """
    command = ["rclone", "sync", source, destination]
    if args is not None:
        command.extend(args)
        
    logger.info(f"Running command: {' '.join(command)}")
    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Capture stdout and stderr in real-time
        for stdout_line in iter(process.stdout.readline, ""):
            logger.debug(stdout_line.strip())
        for stderr_line in iter(process.stderr.readline, ""):
            logger.debug(stderr_line.strip())
        
        process.stdout.close()
        process.stderr.close()
        return_code = process.wait()
        
        if return_code != 0:
            raise subprocess.CalledProcessError(return_code, command)
        
        logger.info(f"Sync completed for {source} to {destination}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error syncing {source} to {destination}: {e}")
        logger.error(f"stdout: {e.stdout}")
        logger.error(f"stderr: {e.stderr}")
    except Exception as e:
        logger.error(f"An error occurred: {e}")

def main():
    """
    Main function to perform the backup process.

    Iterates over the defined backup locations and synchronizes each source directory with its corresponding destination directory using rclone.
    Logs the start and end of the synchronization process for each directory, as well as the total elapsed time for the entire backup process.
    """
    start_time = time.time()
    for source, destination in BACKUP_LOCATIONS.items():
        if source == HOME_DIR:
            ARGS.extend(HOME_ARGS)
        logger.info(f"Syncing {source} to {destination}")
        rclone_sync(source, destination, args=ARGS)
    end_time = time.time()
    elapsed_time = (end_time - start_time) / 60
    logger.info(f"Backup process completed in {elapsed_time:.2f} minutes")

console_output(CONSOLE_OUTPUT)

if __name__ == "__main__":
    main()
