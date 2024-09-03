# Player Transaction Performance in the Top English Football League

This is my very first Data Analysis project with Python. This analyzes how the player transaction of each Club in the top English Football League since 1993 has performed in terms of some easy figures.

## Raw Data:

I obtained the raw data from the [Transmarkt](https://www.transmarkt.co.uk) and [English Premier League](https://www.premierleague.com/) websites. The former provided data with longer history. 


## Data cleaning:

As the raw data are quite messy, cleaning is essential. By importing Pandas, I performed actions such as Dropna, converting from M to million, standardizing club names across csv files, sorting by Club and Year etc. Processed files are then saved as _temp.csv for further analysis.

## Analysis:

The analyses below take place in respect to the net number of players transferred each season.

Analyses begin with two graphs illustrating the average and total expense of each club in player transaction. 

It follows with comparing average income (spending) in transaction versus each league point gained (dropped), and also versus each goal for again and goal against increased for each club, year by year. Scenarios Analysis depicts the matrix showing for how many seasons in actual figures and in percentage that net spending and income relate to league point, goal for and goal against changes, both positively and negatively.

What comes next is the overall correlation between the goal difference and number of forward transferred in, goal difference and number of defenders (Defender + Goalkeeper) transferred in, and Total Passes Difference and number of midfielders bought in.

Finally, the above correlation calculation is repeated for each club respectively. Note that certain clubs with insufficient population data are neglected. And a heat map is drawn accordingly.

## Installation:

1. **Clone the Repository:**

```bash
git clone https://github.com/CharleyYeung/Data_Analysis/Football_Project
```

2. **Create and activate a virtual environment:**

```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

3. **Install the required dependencies:**

```bash
pip install pandas numpy seaborn
```

4. **Ensure all data files are placed in the following directories:**

- `data/raw`: for raw CSV files 

5. **Run the main script in order::**

```bash
python Renaming_preprocess.py
python data_preprocess.py
python main.py
```
