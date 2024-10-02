# Import necessary libraries for PDF generation, image handling, and file operations
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PIL import Image
import urllib.request
import time
import webbrowser
import json
import random
from pathlib import Path
import os
import requests


def sort_monsters(monster_list):
    """
    Sorts the list of monsters based on their size.
    """
    list_length = len(monster_list)
    for i in range(list_length):
        for j in range(list_length - i - 1):
            if monster_list[j][1] < monster_list[j + 1][1]:
                # Swap monsters based on size
                monster_list[j], monster_list[j + 1] = monster_list[j + 1], monster_list[j]
    return monster_list


# Set the name for the cutouts
project_name = input('Enter the name for cutouts: ')
page_number = int(input('Enter pages requested: '))
# Delete all existing files in the cutouts folder
[cutout_file.unlink() for cutout_file in Path("..", "data/output/").glob("*") if cutout_file.is_file()]

# Loop to generate two PDF files with monster cutouts
for sheet_number in range(page_number):
    print(f"Processing sheet {sheet_number + 1}...")

    # Define paths for saving PDFs and reading JSON data
    cutout_folder = os.path.join("..", "output/")
    json_folder = os.path.join("..", "data", 'full monster list.json')

    # Create a new PDF canvas for each sheet
    pdf_canvas = canvas.Canvas(cutout_folder + project_name + str(sheet_number + 1) + ".pdf", pagesize=LETTER)

    # Path to the folder containing monster images
    image_folder = os.path.join("..", "data/images/")  # Go up one level to find the folder
    os.listdir(image_folder)  # Get list of files in the folder

    # Parameters for the layout of the PDF (number of monsters per row and column)
    monsters_per_row, monsters_per_column = 4, 9
    sheet_capacity = monsters_per_row * monsters_per_column / 2  # Total monsters per sheet

    # Lists to categorize monsters by size
    tiny_monsters, small_monsters, normal_monsters, large_monsters, huge_monsters = [], [], [], [], []
    monster_data_list = []

    # Read the JSON file containing the monster list
    with open(json_folder) as json_file:
        monster_data = json.load(json_file)
        monster_index = 0

        # Process each monster in the JSON data
        for monster in monster_data:
            title = monster['title']

            # Remove '(1/2)' from titles
            if '(1/2)' in title:
                title = title.replace('(1/2)', "")

            # Only include monsters not labeled as '(2/2)'
            if '(2/2)' not in title:
                monster_data_list.append([])  # Add new monster entry
                monster_data_list[monster_index].append(title.lower())  # Append monster title in lowercase

                # Extract and categorize the monster's size
                monster_description = str(monster['contents'])
                monster_size_text = monster_description[12:20]
                monster_size_category = 0  # Default size category

                # Categorize the monster based on its size
                if 'Tiny' in monster_size_text:
                    tiny_monsters.append(title.lower())
                elif 'Smal' in monster_size_text:
                    monster_size_category = 1
                    small_monsters.append(title.lower())
                elif 'Larg' in monster_size_text:
                    monster_size_category = 3
                    large_monsters.append(title.lower())
                elif 'Huge' in monster_size_text or 'Garg' in monster_size_text:
                    monster_size_category = 4
                    huge_monsters.append(title.lower())
                else:
                    normal_monsters.append(title.lower())  # If size is not specified, it's a normal monster

                # Append monster size and background image to the list
                monster_data_list[monster_index].append(monster_size_category)
                monster_data_list[monster_index].append(monster['background_image'])

                monster_index += 1

    # Create a dictionary with monster names, their size, and background images
    monster_dict = {monster_data_list[0][0]: {'url': monster_data_list[0][2], 'size': monster_data_list[0][1]}}

    # Update the dictionary with all the monsters from the list
    for i in range(len(monster_data_list)):
        monster_dict.update({monster_data_list[i][0]:{'url': monster_data_list[i][2], 'size': monster_data_list[i][1]}})

    # Sort the monster list alphabetically
    monster_dict = {key: value for key, value in sorted(monster_dict.items())}

    # Initialize variables for the monster selection process
    random_selection = False
    selected_monsters = []  # List of selected monster names
    monster_index = 0
    total_monsters_on_sheet = 0  # Total monsters currently added to the sheet
    print_monsters = []  # List of monsters to print with their URLs and sizes
    temp_monster_list = []
    random_index = 117  # Unused in current logic

    # Start the monster selection process
    while True:
        while True:
            # Display how many monsters can still be added to the sheet
            print(f'You can add {round(sheet_capacity - total_monsters_on_sheet)} more monsters.')

            # Randomly select a monster from the list
            selected_monster_name = monster_data_list[random.randrange(0, len(monster_data_list))][0]
            random_selection = True  # Toggle random selection

            # If random selection is not enabled, ask the user to input the monster name
            if not random_selection:
                selected_monster_name = input('What monster?   ')

            # If the user inputs 'random', enable random selection
            if selected_monster_name == 'random':
                random_selection = True

            # If random selection is enabled, choose a random monster again
            if random_selection:
                selected_monster_name = monster_data_list[random.randrange(0, len(monster_data_list))][0]

            print(selected_monster_name)

            # Display the full list of monsters if 'list' is entered
            if selected_monster_name == 'list':
                print("\nMonster List:")
                print(*monster_dict, sep='\n')
                print()

            # Display the list of large monsters if 'large' is entered
            if selected_monster_name == 'large':
                print("\nLarge Monsters:")
                print(*large_monsters, sep='\n')
                print()

            # Display the list of tiny monsters if 'tiny' is entered
            if selected_monster_name == 'tiny':
                print("\nTiny Monsters:")
                print(*tiny_monsters, sep='\n')
                print()

            # Handle if the selected monster is in the monster list
            if selected_monster_name in monster_dict:
                random_index += 1
                monster_size_factor = 1  # Default size factor for normal monsters

                # Adjust the size factor based on the monster's size category
                if selected_monster_name in (normal_monsters, small_monsters, tiny_monsters):
                    monster_size_factor = 1
                elif selected_monster_name in large_monsters:
                    monster_size_factor = 2
                elif selected_monster_name in huge_monsters:
                    monster_size_factor = 4

                # Check if the monster is too large to fit on the sheet
                if monster_size_factor in (3, 4) and total_monsters_on_sheet == 16:
                    print('Monster is too big for the remaining space.')
                    continue
                else:
                    monster_count = random.randrange(1, 2) * monster_size_factor

                # If not randomly selecting, ask the user for the number of monsters to add
                if not random_selection:
                    while True:
                        try:
                            monster_count = int(input('How many?   ')) * monster_size_factor
                            break
                        except ValueError:
                            print("Invalid input, please enter an integer.")

                # Update the total number of monsters on the sheet
                total_monsters_on_sheet += monster_count
                monster_quantity = int(monster_count / monster_size_factor)  # Calculate actual number of monsters

                # If the total doesn't exceed the sheet size, add the monster to the print list
                if total_monsters_on_sheet <= sheet_capacity:
                    for _ in range(monster_quantity):
                        temp_monster_list.append(selected_monster_name)
                        print_monsters.append([])
                        print_monsters[monster_index].append(
                            monster_dict[selected_monster_name]['url'])  # Add monster image URL
                        print_monsters[monster_index].append(
                            monster_dict[selected_monster_name]['size'])  # Add monster size
                        monster_index += 1

                # If the total exceeds the sheet size, undo the addition
                if total_monsters_on_sheet > sheet_capacity:
                    print(
                        f'Too many monsters, you can only add {round(sheet_capacity - (total_monsters_on_sheet - monster_count))} more.')
                    total_monsters_on_sheet -= monster_count

                # If the sheet is full, exit the loop
                if total_monsters_on_sheet == sheet_capacity:
                    break
                break

            # If the monster isn't in the list, notify the user
            if selected_monster_name not in monster_dict and selected_monster_name != 'list':
                print(f'Sorry, the monster "{selected_monster_name}" is not in our list. Please try again.')

        # Exit the outer loop if the sheet is full
        if total_monsters_on_sheet == sheet_capacity:
            break

    # Capture the start time for performance tracking
    start_time = time.time()
    # Sort the print_monsters list based on some criteria (assumed from earlier code)
    sort_monsters(print_monsters)

    # Remove the size attribute from each monster entry
    for i in range(len(print_monsters)):
        print_monsters[i].pop()

    # Append all monsters into a single list
    for i in range(len(print_monsters) - 1):
        print_monsters[0].append(print_monsters[i + 1][0])

    # Reduce print_monsters to a single flattened list
    print_monsters = print_monsters[0]

    # Initialize variables for handling the monster images and PDF layout
    monster_pictures = []  # List to hold the processed monster images
    page_width, page_height = LETTER  # Page size (LETTER)

    x_positions = []  # List to store x-coordinates for placing images
    y_positions = []  # List to store y-coordinates for placing images
    page_margin = 54  # Page margin in points
    available_width = page_width - (2 * page_margin)
    available_height = page_height - (2 * page_margin)

    picture_counter = 0
    row_index = 0

    # Calculate x and y positions for image grid based on sheet size
    for i in range(monsters_per_row + 1):
        x_positions.append((i * available_width / monsters_per_row) + page_margin)
    x_positions[0] = page_margin
    x_positions[len(x_positions) - 1] = page_width - page_margin

    for j in range(monsters_per_column + 1):
        y_positions.append((j * available_height / monsters_per_column) + page_margin)
    y_positions[0] = page_margin
    y_positions[len(y_positions) - 1] = page_height - page_margin

    # Calculate the size of each image box on the grid
    image_size = (x_positions[1] - x_positions[0]), (y_positions[1] - y_positions[0])

    # Print elapsed time since the start and indicate image creation
    print("--- %s seconds ---" % (time.time() - start_time))
    print('Creating images')

    # Loop through each selected monster and retrieve its data
    for i in range(len(print_monsters)):
        selected_monster_data = list(monster_dict[temp_monster_list[i]].values())
        selected_monsters.append(selected_monster_data)  # Add the monster's data to r list

    # Sort monsters based on size or other criteria
    sort_monsters(selected_monsters)

    # Process each monster's image
    for i in range(len(print_monsters)):
        print(print_monsters[i])

        # Initialize empty list for storing monster image paths and dimensions
        monster_pictures.append([])

        # Define local path for the monster image
        monster_pictures[i].append(image_folder + str(i) + 'picture.png')
        monster_pictures[i].append(str(i) + 'picture.png')

        # If no valid URL is found, use a placeholder image
        if 'https' not in print_monsters[i] or 'imgur' in print_monsters[i]:
            urllib.request.urlretrieve(
                'https://i.pinimg.com/originals/99/99/f0/9999f0683a38d555f7dc726adfc18625.png',
                monster_pictures[i][0]
            )
        else:
            # Download the image from the monster's URL
            req = requests.get(print_monsters[i])
            with open(monster_pictures[i][0], 'wb') as f:
                f.write(req.content)

        # Open the downloaded image and rotate it
        img = Image.open(monster_pictures[i][0])
        img = img.rotate(270, expand=True)  # Rotate image by 270 degrees
        img_info = ImageReader(img)  # Convert to ReportLab ImageReader object
        img_width, img_height = img_info.getSize()  # Get the image dimensions

        # Create a horizontally flipped version of the image
        img_flipped = img.transpose(Image.FLIP_LEFT_RIGHT)

        # Save both the original and flipped images
        img.save(monster_pictures[i][0])
        img_flipped.save(image_folder + '(1)' + monster_pictures[i][1])

        # Append the original image's width and height to the monster_pictures list
        monster_pictures[i].append(img_width)
        monster_pictures[i].append(img_height)

        # Calculate aspect ratios for image placement
        grid_aspect_ratio = (x_positions[1] - x_positions[0]) / (y_positions[1] - y_positions[0])
        grid_aspect_ratio_alternative = (x_positions[1] - x_positions[0]) / (y_positions[2] - y_positions[0])
        image_aspect_ratio = img_width / img_height

        #print(selected_monsters[i][1])  # Print the monster's size category (tiny, small, large, etc.)
        monster_pictures[i].append(selected_monsters[i][1])
        # Adjust image size based on its aspect ratio and the monster's size category
        if selected_monsters[i][1] == 3:  # If the monster is "Large"

            if image_aspect_ratio > grid_aspect_ratio_alternative:
                monster_pictures[i][2] = image_size[0] - 3  # Adjust width
                monster_pictures[i][3] = 1 / (image_aspect_ratio / monster_pictures[i][2])  # Adjust height
            elif image_aspect_ratio < grid_aspect_ratio_alternative:
                monster_pictures[i][3] = image_size[1] * 2  # Adjust height
                monster_pictures[i][2] = image_aspect_ratio * monster_pictures[i][3]  # Adjust width
        else:
            if image_aspect_ratio > grid_aspect_ratio:
                monster_pictures[i][2] = image_size[0] - 3  # Adjust width
                monster_pictures[i][3] = 1 / (image_aspect_ratio / monster_pictures[i][2])  # Adjust height
            elif image_aspect_ratio < grid_aspect_ratio:
                monster_pictures[i][3] = image_size[1]  # Adjust height
                monster_pictures[i][2] = image_aspect_ratio * monster_pictures[i][3]  # Adjust width

    # Print elapsed time since the start and indicate PDF creation
    print("--- %s seconds ---" % (time.time() - start_time))
    print('Creating PDF')

    is_new_row = True
    is_first_large = False
    # Loop through all the monster images until processed
    while picture_counter <= len(print_monsters) - 1:
        column_index = 2
        if monster_pictures[picture_counter][4] in (0, 1, 2, 3):  # If size category is 0-3
            column_index = 1

        if monsters_per_row < 3:  # Ensure minimum column count
            monsters_per_row = 3

        while True:
            # Assign card size based on monster's size category
            if monster_pictures[picture_counter][4] == 3:  # Large monster
                card_width, card_height = 1, 1
                grid_height = 2
                grid_width = 1
                grid_y_spacing = 2
                grid_x_spacing = 1
            elif monster_pictures[picture_counter][4] == 4:  # Huge monster
                card_width, card_height = 2, 2
                grid_height = 1
                grid_width = 2
                grid_y_spacing = 2
                grid_x_spacing = 2
            else:  # Small or regular-sized monster
                grid_height = 1
                grid_width = 1
                grid_y_spacing = 1
                grid_x_spacing = 1
                card_width, card_height = 1, 1

            # Draw the original monster image on the PDF
            pdf_canvas.drawImage(
                monster_pictures[picture_counter][0],
                x_positions[column_index] - card_width * monster_pictures[picture_counter][2] - (
                            0.5 * (image_size[0] - monster_pictures[picture_counter][2])),
                (y_positions[row_index] + 0.5 * (grid_height * image_size[1] - monster_pictures[picture_counter][3])),
                width=(monster_pictures[picture_counter][2] * card_width),
                height=(monster_pictures[picture_counter][3] * card_height),
                mask='auto'
            )

            # Draw the flipped version of the monster image
            pdf_canvas.drawImage(
                (image_folder + '(1)' + monster_pictures[picture_counter][1]),
                x_positions[column_index] + (0.5 * (image_size[0] - monster_pictures[picture_counter][2])),
                y_positions[row_index] + 0.5 * (grid_height * image_size[1] - monster_pictures[picture_counter][3]),
                width=(monster_pictures[picture_counter][2] * card_width),
                height=(monster_pictures[picture_counter][3] * card_height),
                mask='auto'
            )

            # Draw grid lines for the current monster's position
            pdf_canvas.grid(
                [x_positions[column_index - grid_x_spacing], x_positions[column_index], x_positions[column_index + grid_x_spacing]],
                [y_positions[row_index], y_positions[row_index + grid_y_spacing]]
            )

            # Adjust position for small monsters
            if monster_pictures[picture_counter][4] in (0, 1, 2):
                if picture_counter <= len(print_monsters) - 2:
                    if column_index == 1:
                        column_index = 3
                    elif column_index == 3:
                        if is_new_row:
                            column_index = 1
                            row_index += 1
                        else:
                            column_index = 3
                            row_index += 1
                            is_new_row = True

            # Adjust position for large monsters (category 3)
            if monster_pictures[picture_counter][4] == 3:
                if picture_counter <= len(print_monsters) - 2:
                    if monster_pictures[picture_counter + 1][4] == 3 and not is_first_large:
                        column_index = 3
                        is_first_large = True
                    elif monster_pictures[picture_counter + 1][4] == 3 and is_first_large:
                        column_index = 1
                        row_index += 2
                        is_first_large = False

                    if monster_pictures[picture_counter + 1][4] in (0, 1, 2) and column_index == 1:
                        column_index = 3
                        is_new_row = False
                    elif monster_pictures[picture_counter + 1][4] in (0, 1, 2) and column_index == 3:
                        column_index = 1
                        row_index += 2

            # Adjust position for huge monsters (category 4)
            if monster_pictures[picture_counter][4] == 4:
                if picture_counter <= len(print_monsters) - 2:
                    row_index += 2

                    if monster_pictures[picture_counter + 1][4] == 3:
                        column_index = 1
                        is_first_large = False
                    if monster_pictures[picture_counter + 1][4] in (0, 1, 2):
                        column_index = 1

            # Move to the next monster image
            picture_counter += 1

            # Break loop when all monsters have been processed
            if picture_counter == len(print_monsters):
                break

    # Rotate text 90 degrees and add it to the PDF for page numbering
    pdf_canvas.rotate(90)
    pdf_canvas.drawString(54, -(15 + 15), str(temp_monster_list)[int(len(str(temp_monster_list)) / 2):])
    pdf_canvas.drawString(54, -(5 + 15), str(temp_monster_list)[:int(len(str(temp_monster_list)) / 2)])

    # End the current page and show it
    pdf_canvas.showPage()

    # Print elapsed time and remove temporary files
    print("--- %s seconds ---" % (time.time() - start_time))
    [f.unlink() for f in Path(image_folder).glob("*") if f.is_file()]



    # Save the PDF
    pdf_canvas.save()

    # Print the time and open the generated PDF in the browser
    print("--- %s seconds ---" % (time.time() - start_time))
    webbrowser.open_new(r"" + cutout_folder + project_name + str(sheet_number + 1) + ".pdf")


