from PIL import Image, ImageDraw, ImageFont
import re
import os
from .assets import resource_path

def bekesh(
    plate_code: str,
    out_path: str    = None,
    show_img: bool   = False,
    extra_month: str = None,      # Only for 'گ' plates
    extra_year: str  = None       # Only for 'گ' plates
):
    """
    Generate an Iranian license plate image based on code.
    """

    if not isinstance(plate_code, str):
        raise ValueError("plate_code must be a string.")
    if len(plate_code) < 6 or len(plate_code) > 13:
        raise ValueError("plate_code length is invalid. Expected 6-13 characters.")

    data_dir = resource_path('data')
    templates = {
        'normal': os.path.join(data_dir, 'normal.png'),
        'aleph':  os.path.join(data_dir, 'alef.png'),
        'malul':  os.path.join(data_dir, 'malul.png'),
        'teh':    os.path.join(data_dir, 'taxi.png'),
        'ain':    os.path.join(data_dir, 'ain.png'),
        'police': os.path.join(data_dir, 'police.png'),
        'sepah':  os.path.join(data_dir, 'sepah.png'),
        'h':      os.path.join(data_dir, 'h.png'),
        'sh':     os.path.join(data_dir, 'army.png'),
        'g':      os.path.join(data_dir, 'gozar.png'),
        'k':      os.path.join(data_dir, 'k.png'),
        'f':      os.path.join(data_dir, 'SKol.png'),
        'z':      os.path.join(data_dir, 'VDefa.png'),
    }
    font_path = os.path.join(data_dir, 'Plate_font.ttf')
    letter_type   = None
    matched_parts = None

    # List of plate type regular expressions (all raw strings, no replace needed)
    regex_structures = [
        ("malul",  r"^(\d{2})معلول(\d{3})(\d{2,3})$"),
        ("aleph",  r"^(\d{2})الف(\d{3})(\d{2,3})$"),
        ("teh",    r"^(\d{2})ت(\d{3})(\d{2,3})$"),
        ("ain",    r"^(\d{2})ع(\d{3})(\d{2,3})$"),
        ("police", r"^(\d{2})پ(\d{3})(\d{2,3})$"),
        ("sepah",  r"^(\d{2})ث(\d{3})(\d{2,3})$"),
        ("h",      r"^(\d{2})([هـه])(\d{3})(\d{2,3})$"),
        ("sh",     r"^(\d{2})ش(\d{3})(\d{2,3})$"),
        ("g",      r"^(\d{2})گ(\d{3})(\d{2,3})$"),
        ("k",      r"^(\d{2})ک(\d{3})(\d{2,3})$"),
        ("f",      r"^(\d{2})ف(\d{3})(\d{2,3})$"),
        ("z",      r"^(\d{2})ز(\d{3})(\d{2,3})$"),
        ("normal", r"^(\d{2})([آ-ی])(\d{3})(\d{2,3})$"),
    ]

    for l_type, regex in regex_structures:
        match = re.match(regex, plate_code)
        if match:
            letter_type   = l_type
            matched_parts = match.groups()
            break

    if not letter_type:
        raise ValueError("Invalid plate_code format or unsupported plate type.")

    # Plate parts extraction based on type
    if letter_type == "normal":
        number_left, letter, number_right, state_code = matched_parts
    elif letter_type == "h":
        number_left, letter, number_right, state_code = matched_parts
    elif letter_type == "g":
        number_left, number_right, state_code = matched_parts
        if extra_month is None or extra_year is None:
            raise ValueError("For 'گ' (gozar) plates, both extra_month and extra_year must be provided.")
        if letter_type == "g" and plate_code[2] != 'گ':
            raise ValueError("Only 'گ' allowed for this type.")
    elif letter_type in ['sh', 'k', 'f', 'z']:
        number_left, number_right, state_code = matched_parts
    else:
        number_left, number_right, state_code = matched_parts

    if len(state_code) > 2:
        raise ValueError("state_code must be 2-digit.")

    all_numeric = [number_left, number_right, state_code]
    checklist   = all_numeric

    # --- Extra validation: plate numbers (other than state_code) cannot be all zeros ---
    if letter_type == 'normal':
        zero_numbers = [number_left, number_right]
    elif letter_type == 'h':
        zero_numbers = [number_left, number_right]
    elif letter_type == 'g':
        zero_numbers = [number_left, number_right]
    elif letter_type in ['sh', 'k', 'f', 'z']:
        zero_numbers = [number_left, number_right]
    elif letter_type in ['aleph','malul','teh','ain','police','sepah']:
        zero_numbers = [number_left, number_right]
    else:
        zero_numbers = [number_left, number_right]
    # If any number is all zeros (not state_code) => raise error
    for num in zero_numbers:
        if set(num) == {'0'}:
            raise ValueError("Plate numbers (except state code) cannot be all zero.")

    # Digits-only check for all values (including state_code)
    for num in checklist:
        if not num.isdigit():
            raise ValueError("One of number parts is not numeric.")

    layout_base = {
        "font_size": 100, "state_ratio": 1.02, "white_x1_ratio": 0.051, "white_x2_ratio": 0.87,
        "white_y1_ratio": 0.01, "white_y2_ratio": 0.99, "main_offset_x": 10, "num_y_offset": 16,
        "letter_offset_y": -22, "space1": 22, "space2": 22, "state_offset_x": -20, "font_color": "black"
    }
    layout_dict = {
        'normal' : {**layout_base, "font_size": 103, "main_offset_x": 24, "num_y_offset": 17, "font_color": "black", "letter_offset_y": -22},
        'aleph'  : {**layout_base, "font_color": "white", "aleph_space": 120, "main_offset_x": 18},
        'malul'  : {**layout_base, "malul_space": 120, "main_offset_x": 10},
        'teh'    : {**layout_base, "teh_space": 120},
        'ain'    : {**layout_base, "ain_space": 120},
        'police' : {**layout_base, "font_color": "white", "police_space": 120},
        'sepah'  : {**layout_base, "font_color": "white", "sepah_space": 120},
        'h'      : {**layout_base, "font_color": "black", "h_space": 120, "main_offset_x": 24, "num_y_offset": 17, "letter_offset_y": -22, "space1": 100, "space2": 22},
        'sh'     : {**layout_base, "font_color": "black", "sh_space": 120},
        'g'      : {**layout_base, "font_color": "black", "gozar_space": 120, "num_y_offset": 16},
        'k'      : {**layout_base, "font_color": "black", "k_space": 120},
        'f'      : {**layout_base, "font_color": "white", "SKol_space": 120},
        'z'      : {**layout_base, "font_color": "white", "VDefa_space": 120},
    }
    layout = layout_dict[letter_type]

    template_path = templates[letter_type]
    if not os.path.isfile(template_path):
        raise FileNotFoundError(f"Template file '{template_path}' not found.")
    img = Image.open(template_path)
    width, height = img.size
    draw = ImageDraw.Draw(img)

    # Calculate white border & drawing area
    white_x1    = int(width * layout["white_x1_ratio"])
    white_x2    = int(width * layout["white_x2_ratio"])
    white_y1    = int(height * layout["white_y1_ratio"])
    white_y2    = int(height * layout["white_y2_ratio"])
    white_width = white_x2 - white_x1

    # Select font and main vertical offset
    font_main     = ImageFont.truetype(font_path, layout["font_size"])
    font_state    = ImageFont.truetype(font_path, int(layout["font_size"] * layout["state_ratio"]))
    main_h_center = white_y1 + ((white_y2 - white_y1) - layout["font_size"]) // 2

    persian_letters_lower = ['د', 'ذ', 'ر', 'ز', 'ط', 'ظ', 'م', 'ن']

    only_number_types = ['aleph','malul','teh','ain','police','sepah','sh','g','k','f','z']

    # ----------- DRAWING LOGIC PER PLATE TYPE -----------
    if letter_type == 'h':
        # Temporary (mowaghat): just numbers, without center letter
        num_left_bbox  = draw.textbbox((0, 0), number_left, font=font_main)
        num_right_bbox = draw.textbbox((0, 0), number_right, font=font_main)
        main_w         = (num_left_bbox[2] - num_left_bbox[0]) + layout["space1"] + (num_right_bbox[2] - num_right_bbox[0])
        main_x         = white_x1 + (white_width - main_w) // 2 - layout["main_offset_x"]
        num_y          = main_h_center + layout["num_y_offset"]
        num_left_x     = main_x
        num_right_x    = num_left_x + (num_left_bbox[2] - num_left_bbox[0]) + layout["space1"]
        draw.text((num_left_x, num_y), number_left, font=font_main, fill=layout["font_color"])
        draw.text((num_right_x, num_y), number_right, font=font_main, fill=layout["font_color"])

    elif letter_type in ['sh','g','k','f','z']:
        # Two numbers with specific space between, for military, gozar, etc.
        num_left_bbox  = draw.textbbox((0, 0), number_left, font=font_main)
        num_right_bbox = draw.textbbox((0, 0), number_right, font=font_main)
        space_key      = [k for k in ['sh_space','gozar_space','k_space','SKol_space','VDefa_space'] if k in layout]
        side_space     = layout.get(space_key[0], 100) if space_key else 100
        main_w         = (num_left_bbox[2] - num_left_bbox[0]) + side_space + (num_right_bbox[2] - num_right_bbox[0])
        main_x         = white_x1 + (white_width - main_w) // 2 - layout["main_offset_x"]
        num_y          = main_h_center + layout["num_y_offset"]
        num_left_x     = main_x
        num_right_x    = num_left_x + (num_left_bbox[2] - num_left_bbox[0]) + side_space
        draw.text((num_left_x, num_y), number_left, font=font_main, fill=layout["font_color"])
        draw.text((num_right_x, num_y), number_right, font=font_main, fill=layout["font_color"])

    elif letter_type in ['aleph','malul','teh','ain','police','sepah']:
        # Classic two-number layout (specific plate types)
        num_left_bbox  = draw.textbbox((0, 0), number_left, font=font_main)
        num_right_bbox = draw.textbbox((0, 0), number_right, font=font_main)
        space_key      = [k for k in ['aleph_space','malul_space','teh_space','ain_space','police_space','sepah_space'] if k in layout][0]
        side_space     = layout.get(space_key, 100)
        main_w         = (num_left_bbox[2] - num_left_bbox[0]) + side_space + (num_right_bbox[2] - num_right_bbox[0])
        main_x         = white_x1 + (white_width - main_w) // 2 - layout["main_offset_x"]
        num_y          = main_h_center + layout["num_y_offset"]
        num_left_x     = main_x
        num_right_x    = num_left_x + (num_left_bbox[2] - num_left_bbox[0]) + side_space
        draw.text((num_left_x, num_y), number_left, font=font_main, fill=layout["font_color"])
        draw.text((num_right_x, num_y), number_right, font=font_main, fill=layout["font_color"])

    else:
        # Normal civilian plates
        number_left, letter, number_right, state_code = matched_parts
        num_left_bbox  = draw.textbbox((0, 0), number_left, font=font_main)
        letter_bbox    = draw.textbbox((0, 0), letter, font=font_main)
        num_right_bbox = draw.textbbox((0, 0), number_right, font=font_main)
        main_w = (num_left_bbox[2] - num_left_bbox[0]) + layout["space1"] + \
                 (letter_bbox[2] - letter_bbox[0]) + layout["space2"] + \
                 (num_right_bbox[2] - num_right_bbox[0])
        main_x          = white_x1 + (white_width - main_w) // 2 - layout["main_offset_x"]
        num_y           = main_h_center + layout["num_y_offset"]
        num_left_x      = main_x
        letter_x        = num_left_x + (num_left_bbox[2] - num_left_bbox[0]) + layout["space1"]
        num_right_x     = letter_x + (letter_bbox[2] - letter_bbox[0]) + layout["space2"]
        letter_for_draw = letter
        letter_y        = num_y + layout["letter_offset_y"]

        # Special positioning for some Persian letters
        if letter == 'ل':
            letter_y += 18
        if letter == 'م':
            letter_y -= 12
        if letter_for_draw in persian_letters_lower:
            letter_y += 15

        draw.text((num_left_x, num_y), number_left, font=font_main, fill=layout["font_color"])
        draw.text((letter_x, letter_y), letter_for_draw, font=font_main, fill=layout["font_color"])
        draw.text((num_right_x, num_y), number_right, font=font_main, fill=layout["font_color"])

    # ----------- Draw Province/State Code -----------
    if letter_type == 'g':
        # Special style for 'گذر'
        if state_code == '00':
            state_font_size = int(layout["font_size"] * 0.78)
        else:
            state_font_size = int(layout["font_size"] * 0.60)
        font_state_g = ImageFont.truetype(font_path, state_font_size)

        state_x1     = int(width * layout["white_x2_ratio"])
        state_x2     = width
        state_y1     = 0
        state_y2     = height
        state_w      = state_x2 - state_x1
        state_h      = state_y2 - state_y1
        state_bbox   = draw.textbbox((0, 0), state_code, font=font_state_g)
        state_text_w = state_bbox[2] - state_bbox[0]
        state_text_h = state_bbox[3] - state_bbox[1]
        state_text_x = state_x1 + (state_w - state_text_w)//2 + layout["state_offset_x"]
        state_text_y = state_y1 + (state_h - state_text_h)//2 + 8
        draw.text((state_text_x, state_text_y), state_code, font=font_state_g, fill=layout["font_color"])

        font_extra = ImageFont.truetype(font_path, int(layout["font_size"] * 0.46))
        extra_text = f"{extra_month}/{extra_year}"
        ext_bbox   = draw.textbbox((0, 0), extra_text, font=font_extra)
        ext_w      = ext_bbox[2] - ext_bbox[0]
        ext_x      = state_x1 + (state_w - ext_w)//2 + layout["state_offset_x"] - 7
        ext_y      = state_text_y + state_text_h + 30
        draw.text((ext_x, ext_y), extra_text, font=font_extra, fill=layout["font_color"])

    else:
        # Draw state code normally
        state_x1     = int(width * layout["white_x2_ratio"])
        state_x2     = width
        state_y1     = 0
        state_y2     = height
        state_w      = state_x2 - state_x1
        state_h      = state_y2 - state_y1
        state_bbox   = draw.textbbox((0,0), state_code, font=font_state)
        state_text_w = state_bbox[2] - state_bbox[0]
        state_text_h = state_bbox[3] - state_bbox[1]
        state_text_x = state_x1 + (state_w - state_text_w)//2 + layout["state_offset_x"]
        state_text_y = state_y1 + (state_h - state_text_h)//2 + (4 if state_code != '00' else -10)
        draw.text((state_text_x, state_text_y), state_code, font=font_state, fill=layout["font_color"])

    if out_path:
        img.save(out_path)
    if show_img:
        img.show()
    return img

# Github.com/RezaGooner
