import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from football_project.get_paths import get_yaml_path, get_general_config,get_cleaned_file_paths, get_cleaned_folder_path, get_analysis_folder_path
from football_project.utils import *
import yaml
import os


path_config = get_yaml_path()
general_config = get_general_config()


ready_file_league = path_config['ready_files']['league']
cleaned_folder = get_cleaned_folder_path('cleaned')
ready_file_path_league = os.path.join(cleaned_folder, ready_file_league)
input_path_league = get_cleaned_file_paths(path_config['ready_files']['league'])
league_data = pd.read_csv(input_path_league)
df_league = pd.DataFrame(league_data)
input_path_combined = get_cleaned_file_paths(path_config['ready_files']['combined'])
combined_data =pd.read_csv(input_path_combined)
df_combined = pd.DataFrame(combined_data)
input_path_balance = get_cleaned_file_paths(path_config['ready_files']['balance'])
balance_data =pd.read_csv(input_path_balance)
df_balance = pd.DataFrame(balance_data)
input_path_passes = get_cleaned_file_paths(path_config['ready_files']['passes'])
passes_data =pd.read_csv(input_path_passes)
df_passes = pd.DataFrame(passes_data)


analysis_folder = get_analysis_folder_path('analysis')
top_clubs = int(general_config['top_clubs'])


averages = df_league[['Goal For', 'Pts']].mean()

# Bar Chart of Basic Statistics
plt.figure(figsize=(10, 6),num='Average Goals and Points in PL')
averages.plot(kind='bar')
plt.title('Average Goals and Points in Premier League')
plt.xlabel('Overall Statistics')
plt.ylabel('Average Value')
plt.xticks(rotation=0)
for i, v in enumerate(averages):
    plt.text(i, v, f'{v:.2f}', ha='center', va='bottom')

output_path_stats = os.path.join(analysis_folder, 'stats.png')
plt.savefig(output_path_stats)
print("Plot saved as stats.png")

plt.close()

# Box plot of Goal Differences

print("Creating goal difference boxplot...")
plt.figure(figsize=(15, 10), num='Goal Difference Distribution')
sns.boxplot(x='Club', y='+/-', data=df_league)
plt.title('Distribution of Goal difference for Each Club')
plt.xlabel('Club')
plt.ylabel('Goal Difference')
plt.xticks(rotation=90) 
plt.axhline(y=0, color='r', linestyle='--', linewidth=1)
plt.tight_layout()
output_file = os.path.join(analysis_folder, 'goal_diff_boxplot.png')
plt.savefig(output_file)
print(f"Box plot saved as {output_file}")
plt.close() 

print("Calculating average points...")
avg_points = df_combined.groupby('Club')['Pts'].mean().sort_values(ascending=False)
print("Top clubs by points:", avg_points.head())

top_n = int(general_config['top_clubs'])
top_clubs_by_points = avg_points.head(top_n).index.tolist()
print("Top clubs:", top_clubs_by_points)

df_top_clubs = df_combined[df_combined['Club'].isin(top_clubs_by_points)]
print("Shape of df_top_clubs:", df_top_clubs.shape)

median_balance = df_top_clubs.groupby('Club')['Balance'].median().sort_values(ascending=False)
print("Median balance:", median_balance)

df_top_clubs = df_top_clubs.copy()
df_top_clubs['Inverted_Balance'] = df_top_clubs['Balance'] * 1

print("Creating net expense boxplot...")
plt.figure(figsize=(20, 10), num=f'Net Expense Distribution for Top {top_n} Clubs')
ax = sns.boxplot(x='Club', y='Inverted_Balance', data=df_top_clubs, order=top_clubs_by_points)
sns.stripplot(x='Club', y='Inverted_Balance', data=df_top_clubs, order=top_clubs_by_points, color=".25", alpha=0.5, jitter=True)

plt.axhline(y=0, color='r', linestyle='--', alpha=0.5)

y_min = df_top_clubs['Inverted_Balance'].min() - 0.1 * abs(df_top_clubs['Inverted_Balance'].min())
y_max = df_top_clubs['Inverted_Balance'].max() + 0.1 * abs(df_top_clubs['Inverted_Balance'].max())
plt.ylim(y_max, y_min)

ax.yaxis.set_major_formatter(plt.FuncFormatter(millions_formatter))

plt.title(f'Distribution of Net Expense for Top {top_n} Clubs by Average Points')
plt.xlabel('Club')
plt.ylabel('Net Expense (Million €)')
plt.xticks(rotation=45, ha='right')

plt.tight_layout()

output_file = os.path.join(analysis_folder, f'top_{top_n}_club_net_expense_boxplot.png')
plt.savefig(output_file, dpi=300, bbox_inches='tight')
print(f"Top {top_n} clubs net expense box plot saved as {output_file}")
plt.close()


clubs = df_combined['Club'].unique()
years = df_combined['Year'].unique()
analysis_results = ''
year_by_year_results = ''


for club in clubs:
    club_data = df_combined[df_combined['Club'] == club]
    
    total_spending = 0
    total_pts_diff = 0
    total_gf_diff = 0
    total_ga_diff = 0
    years_count = 0
    
    # Calculate overall statistics 
    for i, row in club_data.iterrows():
        balance = row['Balance']
        pts_diff = row['Pts Diff']
        gf_diff = row['GF Diff']
        ga_diff = row['GA Diff']
        
        if not pd.isna(balance):
            total_spending += balance
            years_count += 1
        
        if not pd.isna(pts_diff):
            total_pts_diff += pts_diff
        
        if not pd.isna(gf_diff):
            total_gf_diff += gf_diff
        
        if not pd.isna(ga_diff):
            total_ga_diff += ga_diff
    

    avg_spending_per_year = total_spending / years_count if years_count > 0 else 0
    avg_pts_diff_per_year = total_pts_diff / years_count if years_count > 0 else 0
    avg_gf_diff_per_year = total_gf_diff / years_count if years_count > 0 else 0
    avg_ga_diff_per_year = total_ga_diff / years_count if years_count > 0 else 0
    
    analysis_results += f"\nOverall Analysis for {club} ({years_count} years):\n"
    analysis_results += f"  Average yearly spending: {format_value(avg_spending_per_year)}\n"
    analysis_results += f"  Average yearly points difference: {avg_pts_diff_per_year:.2f}\n"
    analysis_results += f"  Average yearly goals for difference: {avg_gf_diff_per_year:.2f}\n"
    analysis_results += f"  Average yearly goals against difference: {avg_ga_diff_per_year:.2f}\n"
    
    if total_pts_diff != 0:
        overall_cost_per_point = total_spending / total_pts_diff
        analysis_results += f"  Overall cost per point: {format_value(overall_cost_per_point)}\n"
    if total_gf_diff != 0:
        overall_cost_per_gf = total_spending / total_gf_diff
        analysis_results += f"  Overall cost per goal for: {format_value(overall_cost_per_gf)}\n"
    if total_ga_diff != 0:
        overall_cost_per_ga = total_spending / total_ga_diff
        analysis_results += f"  Overall cost per goal against: {format_value(overall_cost_per_ga)}\n"
    

    year_by_year_results += f"\n{club} Year by year analysis:\n"
    for year in years:
        year_data = club_data[club_data['Year'] == year]
        
        if not year_data.empty:
            balance = year_data['Balance'].values[0]
            pts_diff = year_data['Pts Diff'].values[0]
            gf_diff = year_data['GF Diff'].values[0]
            ga_diff = year_data['GA Diff'].values[0]
            
            cost_per_point = balance / pts_diff if pts_diff != 0 and not pd.isna(pts_diff) else np.nan
            cost_per_GF = balance / gf_diff if gf_diff != 0 and not pd.isna(gf_diff) else np.nan
            cost_per_GA = balance / ga_diff if ga_diff != 0 and not pd.isna(ga_diff) else np.nan
            
            formatted_results = [
                format_result(cost_per_point, balance, pts_diff, 'Point'),
                format_result(cost_per_GF, balance, gf_diff, 'GF'),
                format_result(cost_per_GA, balance, ga_diff, 'GA')
            ]
            
            valid_results = [result for result in formatted_results if result is not None]
            if valid_results:
                year_by_year_results += f"Year {year}:\n"
                for result in valid_results:
                    year_by_year_results += f"  {result}\n"

full_analysis = analysis_results + "\n" + year_by_year_results

output_file_text = os.path.join(analysis_folder, 'club_analysis_results.txt')
with open(output_file_text, 'w') as f:
    f.write(full_analysis)

print(f"Analysis results saved to {output_file_text}")

# Scenario Analysis and Stacked Percentage Bar Plot

fig, ax = plt.subplots(figsize=(15, 10), num='Scenario Analysis for Each Club')
colors = plt.get_cmap('tab20')(np.linspace(0, 1, 12))
bottom = np.zeros(len(clubs))

scenarios = general_config['scenarios']
all_club_scenarios = analyze_club_scenarios(df_combined, scenarios.copy())


total_values = np.zeros(len(clubs))

for club in clubs:
    club_data = df_combined[df_combined['Club'] == club]
    club_scenarios = analyze_club_scenarios(club_data, scenarios.copy())
    club_index = np.where(clubs == club)[0][0]
    total_values[club_index] = sum(club_scenarios.values())

for i, scenario in enumerate(all_club_scenarios.keys()):
    values = []
    for club in clubs:
        club_data = df_combined[df_combined['Club'] == club]
        club_scenarios = analyze_club_scenarios(club_data, scenarios.copy())
        values.append(club_scenarios[scenario])
    
    percentage_values = [v / total * 100 if total > 0 else 0 for v, total in zip(values, total_values)]
    
    ax.bar(clubs, percentage_values, bottom=bottom, label=scenario, color=colors[i])
    bottom += percentage_values

ax.set_title('Scenario Analysis for Each Club (Stacked Percentage)', fontsize=16)
ax.set_xlabel('Clubs', fontsize=12)
ax.set_ylabel('Percentage of Years (%)', fontsize=12)
ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)
plt.xticks(rotation=90)
plt.ylim(0, 100) 
plt.tight_layout()

output_file_plot = os.path.join(analysis_folder, 'scenario_analysis_percentage_plot.png')
plt.savefig(output_file_plot, dpi=300, bbox_inches='tight')
print(f"Scenario analysis percentage plot saved as {output_file_plot}")
plt.close()

# Compare the transfer window operation on each position and the performance


df_merged = pd.merge(df_balance, df_passes, on=['Club', 'Year'])
df_merged = pd.merge(df_merged, df_league, on=['Club', 'Year'])

df_merged['defender_goalkeeper'] = df_merged['defender'] + df_merged['goalkeeper']

df_analysis = df_merged[['forward', 'midfielder', 'defender_goalkeeper', 'GF Diff', 'GA Diff', 'Total Passes Diff']]

correlation_matrix = df_analysis.corr()

GF_FW_corr = correlation_matrix.loc['GF Diff', 'forward']
ga_defender_goalkeeper_corr = correlation_matrix.loc['GA Diff', 'defender_goalkeeper']
passes_midfielder_corr = correlation_matrix.loc['Total Passes Diff', 'midfielder']

print(f"Correlation between GF Diff and Forward: {GF_FW_corr}")
print(f"Correlation between GA Diff and Defender + Goalkeeper: {ga_defender_goalkeeper_corr}")
print(f"Correlation between Total Passes Diff and Midfielder: {passes_midfielder_corr}")




# Create a function to calculate correlations for each club

min_seasons = general_config['min_seasons']
season_counts = df_league['Club'].value_counts()
valid_clubs = season_counts[season_counts >= min_seasons].index.tolist()

columns_to_correlate = ['forward', 'midfielder', 'defender_goalkeeper', 'GF Diff', 'GA Diff', 'Total Passes Diff']
club_correlations = df_merged.groupby('Club')[columns_to_correlate].apply(lambda x: calculate_club_correlations(x, min_seasons))

club_correlations = club_correlations.dropna()


plt.figure(figsize=(15, 10), num='Correlation Heatmap')
heatmap = sns.heatmap(club_correlations, annot=True, cmap='coolwarm', center=0)
plt.xticks(rotation=0, ha='center')
plt.yticks(rotation=0, ha='right')
plt.suptitle(f'Correlations by Club (Staying in Minimum {min_seasons} seasons in PL)', fontsize=16, y=0.95)
plt.tight_layout(rect=[0, 0.03, 1, 0.95]) 

output_file_corr = os.path.join(analysis_folder, 'scenario_analysis_corr.png')
plt.savefig(output_file_corr, dpi=300, bbox_inches='tight')
plt.close()