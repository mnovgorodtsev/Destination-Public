from matplotlib import pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.patches as mpatches


def plot_map(tiles, selected_region):
    x_min, x_max = 2000000, 7500000
    y_min, y_max = 1300000, 5500000

    cmap = plt.cm.viridis
    norm = mcolors.Normalize(vmin=tiles['Algorytm'].min(), vmax=tiles['Algorytm'].max())
    fig, ax = plt.subplots(figsize=(20, 15))

    tiles.plot(ax=ax, column='Algorytm', edgecolor='black', cmap=cmap, legend=False, linewidth=0.5)

    selected_tile = tiles[tiles['NUTS_NAME'] == selected_region]
    selected_tile.plot(ax=ax, color='red', edgecolor='black', linewidth=0.5, legend=True)

    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=ax)
    cbar.set_ticks([norm.vmin, norm.vmax / 2, norm.vmax])
    cbar.set_ticklabels(['Niepolecane', 'Neutralne', 'Polecane'])
    red_patch = mpatches.Patch(color='red', label='Wybrany region')
    ax.legend(handles=[red_patch], loc='upper right')

    ax.set_title('Wizualizacja algorytmu', fontsize=16)
    ax.set_xlabel('Współrzędna X', fontsize=14)
    ax.set_ylabel('Współrzędna Y', fontsize=14)

    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)

    return fig


def show_top_results(tiles, merged_df):
    top_5_tiles = tiles.sort_values(by='Algorytm', ascending=False).head(5)

    top_5_regions = top_5_tiles['NAME_LATN'].values
    top_5_data = merged_df[merged_df['Region'].isin(top_5_regions)]
    top5_df = top_5_data.drop_duplicates(subset=['Region'])
    top5_df = top5_df.drop(columns=['Latitude', 'Longitude', 'NUTS_ID', 'CNTR_CODE'])
    top5_df = top5_df.set_index('Region')

    return top5_df


