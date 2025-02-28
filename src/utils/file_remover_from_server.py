import os

def remove_file_from_server(file_path, basename):
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"{basename} has been removed from storage successfully!")
    else:
        print(f"{basename} does not exist in the storage.")