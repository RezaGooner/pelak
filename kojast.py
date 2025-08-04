import os
from .assets import resource_path

def kojast(state_code, letter, txt_file_path="city_plateinfo.txt"):
    """
    Returns the city name for an Iranian license plate, given the state code and the middle letter.
    Args:
        state_code (str): 2-digit state code, e.g. "13"
        letter (str): Persian letter, e.g. "ب"
        txt_file_path (str): Data file name or absolute/relative path

    Returns:
        str: The matching city name

    Raises:
        ValueError: If the city is not found, or the file is missing.
    """
    try:
        # Resolve the data directory path
        data_dir = resource_path('data')
        file_path = txt_file_path
        # If the path is not absolute, look for it in the data directory
        if not os.path.isabs(file_path):
            file_path = os.path.join(data_dir, txt_file_path)
        
        with open(file_path, encoding='utf-8') as f:
            for line in f:
                parts = [x.strip() for x in line.strip().split(',')]
                if len(parts) != 3:
                    continue  # Skip malformed lines
                line_letter, line_code, city = parts
                if line_letter == letter and line_code == state_code:
                    return city
    except FileNotFoundError:
        raise ValueError(f"File {file_path} not found.")
    
    raise ValueError("City not found for the given state code and letter.")


# RezaGooner
