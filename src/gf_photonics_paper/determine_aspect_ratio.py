def width_and_height(num_lines_code, max_characters_per_line):
    """Determines the width and height of a figure for plotting side-by-side next to code
    based on the number of lines of code and the maximum characters per line."""
    width = 473 - (max_characters_per_line-49)*8.5
    height = 370* (num_lines_code+2)/(17+2) 
    global_scale = 1
    width *= global_scale
    height *= global_scale
    return width, height