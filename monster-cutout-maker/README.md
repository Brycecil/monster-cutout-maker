# Monster Cutout Maker

This project generates PDF sheets with monster cutouts for tabletop role-playing games.

## Project Structure

```
monster-cutout-maker/
├── src/
│   └── monster_cutout_maker.py
├── data/
│   └── full_monster_list.json
├── output/
│   └── .gitkeep
├── requirements.txt
├── README.md
├── .gitignore
└── LICENSE
```

## Files and Directories

1. `src/monster_cutout_maker.py`: The main Python script for generating monster cutouts.
2. `data/full_monster_list.json`: JSON file containing the full list of monsters.
3. `output/`: Directory where generated PDFs will be saved.
4. `requirements.txt`: List of Python dependencies.
5. `README.md`: Project documentation and usage instructions.
6. `.gitignore`: Specifies intentionally untracked files to ignore.
7. `LICENSE`: The license for your project (e.g., MIT License).

## Setup and Usage

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/monster-cutout-maker.git
   cd monster-cutout-maker
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the script:
   ```
   python src/monster_cutout_maker.py
   ```

4. Follow the prompts to enter the project name and number of pages.

5. Generated PDFs will be saved in the `output/` directory.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the [MIT License](LICENSE).