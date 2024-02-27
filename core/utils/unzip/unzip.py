import zipfile

def unzip(path_to_zip_file:str, output_dir:str):
    with zipfile.ZipFile(path_to_zip_file, 'r') as zip_ref:
        zip_ref.extractall(output_dir)