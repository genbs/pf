import pymupdf as fitz

def parse_pdf(path, columns=[], interesting_area=[0, 0, -1, -1], first_page_interesting_area=None, pages=None, required_columns=[], possible_multiple_rows=[], stop_fn=None):
    """
    Parses a PDF file and extracts text values from specified columns within a given area.

    Args:
        path (str): The path to the PDF file.
        columns (dict): A dictionary mapping column names to their x-coordinate ranges.
        interesting_area (list): A list representing the area of the page to search for text values. Format: [x1, y1, x2, y2].
        first_page_interesting_area (list): A list representing the area of the first page to search for text values. Format: [x1, y1, x2, y2].
        pages (list or number): A list representing the range of pages to parse. Format: [start_page, end_page].
        required_columns (list): A list of column names that must be present in each extracted value.
        possible_multiple_rows (list): A list of column names that, if present together, indicate a possible multiple-row value.
        stop_fn (function): A function that takes a current value and list of extracted values and returns True if the parsing should stop.

    Returns:
        list: A list of dictionaries, where each dictionary represents a row of extracted values. The keys of the dictionaries are the column names, and the values are the extracted text values.

    """


    doc = fitz.open(path)
    pages = [1, -1] if pages is None else ([pages, -1] if isinstance(pages, int) else pages)
    pages[0] = pages[0] if pages[0] != -1 else doc.page_count
    pages[1] = pages[1] if pages[1] != -1 else doc.page_count

    if len(required_columns) == 0:
        required_columns = columns.keys()

    values = []

    
    for page_num, page in enumerate(doc):
        page_num += 1
        if page_num < pages[0] or page_num > pages[1]:
            continue

        area = get_area(page.rect.width, page.rect.height, first_page_interesting_area if page_num == 1 and first_page_interesting_area else interesting_area)

        dict = page.get_text("dict")

        for block in dict["blocks"]:
            if "lines" not in block:
                continue

            value = {}
            for line in block["lines"]:
                for span in line["spans"]:
                    text = span["text"].strip()
                    bbox = span["bbox"]

                    if is_within_bbox(bbox, area) != True:
                        continue

                    x = bbox[2]
                    #print('X: ', x, 'Text: ', text)
                    for key, (x1, x2) in columns.items():
                        if x >= x1 and x <= x2 and text != "":
                            if key not in value:
                                value[key] = ""
                            value[key] += (" " if value[key] else "") + text

            is_possible_multiple_rows = len(possible_multiple_rows) > 0 and list(value.keys()) == possible_multiple_rows
            # if is_possible_multiple_rows:
            #     print('is_possible_multiple_rows', value)

            # validation
            if not all(k in value for k in required_columns) and not is_possible_multiple_rows:
                continue

            # Add "possible_multiple_rows" values to the last row
            if is_possible_multiple_rows:
                if len(values) == 0:
                    continue
                last_index = len(values) - 1
                last_value = values[last_index]
                for k in possible_multiple_rows:
                    last_value[k] += " " + value[k]
                values[last_index] = last_value

            else:
                # add empty values for missing columns
                for k in columns.keys():
                    if k not in value:
                        value[k] = ""

                values.append(value)
                if stop_fn and stop_fn(value, values):
                    doc.close()
                    return values
    
    doc.close()
    return values

def get_area(page_width, page_height, interesting_area):
    interesting_area[0] = interesting_area[0] if interesting_area[0] != -1 else page_width
    interesting_area[1] = interesting_area[1] if interesting_area[1] != -1 else page_height
    interesting_area[2] = interesting_area[2] if interesting_area[2] != -1 else page_width
    interesting_area[3] = interesting_area[3] if interesting_area[3] != -1 else page_height

    return interesting_area

def is_within_bbox(bbox, area):
    return (bbox[0] >= area[0] and
            bbox[1] >= area[1] and
            bbox[2] <= area[2] and
            bbox[3] <= area[3])