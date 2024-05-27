import os
import shutil
import time
import argparse
import logging
from filecmp import dircmp

def sync_folders(source, replica, log_file):
    def compare_and_sync(source_dir, replica_dir):
        comparison = dircmp(source_dir, replica_dir)

        #Copy new/updated files from source to replica
        for name in comparison.left_only + comparison.diff_files:
            src_path = os.path.join(source_dir, name)
            replica_path = os.path.join(replica_dir, name)
            if os.path.isdir(src_path):
                shutil.copytree(src_path, replica_path)
                log_operation(f"Copied directory from: {src_path} to: {replica_path}")
            else:
                shutil.copy2(src_path, replica_path)
                log_operation(f"Copied file from: {src_path} to: {replica_path}")

        #Remove files and directories from replica that are not in source
        for name in comparison.right_only:
            replica_path = os.path.join(replica_dir, name)
            if os.path.isdir(replica_path):
                shutil.rmtree(replica_path)
                log_operation(f"Removed directory {replica_path}")
            else:
                os.remove(replica_path)
                log_operation(f"Removed file {replica_path}")

        #Recursively sync subdirectories
        for subdir in comparison.common_dirs:
            compare_and_sync(os.path.join(source_dir, subdir), os.path.join(replica_dir, subdir))

    #Sync logfile with the operation executed
    def log_operation(message):
        logging.info(message)
        print(message)
    
    #Check for source directory
    if not os.path.exists(source):
        log_operation(f"Error: Source directory '{source}' does not exist.")
        return

    #Check/Create for replica directory
    if not os.path.exists(replica):
        os.makedirs(replica)
        log_operation(f"Created directory {replica}")

    compare_and_sync(source, replica)

def main():
    parser = argparse.ArgumentParser(description="Synchronize two folders.")
    parser.add_argument("source")
    parser.add_argument("replica")
    parser.add_argument("interval", type=int)
    parser.add_argument("log_file")
    args = parser.parse_args()
    
    ##Check/Create for logfile in the args directory
    log_directory = os.path.dirname(args.log_file)
    if log_directory and not os.path.exists(log_directory):
        os.makedirs(log_directory)

    logging.basicConfig(filename=args.log_file, level=logging.INFO, format='%(asctime)s - %(message)s')

    #Lop Start with interval in seconds provided in args
    while True:
        sync_folders(args.source, args.replica, args.log_file)
        time.sleep(args.interval)

if __name__ == "__main__":
    main()
