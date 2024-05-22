import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def plot_mut_total_counts(tot_csv_df, name="total_mutations"):
    """
    Plots a bar chart of mutations counts per sample. This includes coding and non coding
    
    Parameters:
        df (pd.DataFrame): The input DataFrame containing the data.
        target_columns (list): A list of column names, where the first element is the label column
                               and the second element is the samples column.
        csv_filename (str, optional): Filename for CSV export. If None, no export is done.
    """
    df= pd.read_csv(tot_csv_df, comment='#')
    target_columns=["so","samples"]
    # Extract the target columns
    labels_col, samples_col = target_columns
    
    # Split the samples column into individual items
    df[samples_col] = df[samples_col].str.split(';')
    
    # Explode the DataFrame to have one sample per row
    df_exploded = df.explode(samples_col)
    
    # Count the occurrences of each sample
    sample_counts = df_exploded.groupby(samples_col).size().reset_index(name='count')
    
    # Plot the bar chart using Plotly
    fig = px.bar(sample_counts, x=samples_col, y='count', title='Sample Counts', labels={samples_col: 'Sample', 'count': 'Count'})
    fig.write_image(f"./results/{name}.png")
    
    # Export to CSV if filename is provided
    sample_counts.to_csv(f"./results/{name}.csv", index=False)



# Plots mutations ontology per sample as a stacked plot.  
def plot_mut_ontology(tot_csv_df, name=""):
    """
    Plots a bar chart of mutations ontology counts per sample.
    
    Parameters:
        df (pd.DataFrame): The input DataFrame containing the data.
        csv_filename (str, optional): Filename for CSV export. If None, no export is done.
    """
    df = pd.read_csv(tot_csv_df, comment='#',usecols=['so', 'samples'])
    
    print("Parsing VCF...")
    # Create a list to store parsed data
    parsed_data = []

    # Iterate over each row of the DataFrame
    for index, row in df.iterrows():
        mutation_type = row['so']
        samples = row['samples'].split(';')
        for sample in samples:
            parsed_data.append({'Mutation_Type': mutation_type, 'Sample_Name': sample})

    # Create a DataFrame from the parsed data
    df_parsed = pd.DataFrame(parsed_data)

    # Pivot the DataFrame to obtain the summary
    summary_df = df_parsed.pivot_table(index='Sample_Name', columns='Mutation_Type', aggfunc='size', fill_value=0)

    # Display the summary DataFrame
    print("Generating figure...")
    
    fig = go.Figure()

    # Add traces for each mutation type
    for mutation_type in summary_df.columns:
        fig.add_trace(go.Bar(
            x=summary_df.index,
            y=summary_df[mutation_type],
            name=mutation_type
        ))

    # Update layout
    fig.update_layout(
        barmode='stack',
        xaxis_title='Sample Names',
        yaxis_title='Count',
        title='Mutation Counts per Sample'
    )

    # Show the plot
    fig.write_image(f"./results/{name}_mutations_ontology.png",width=800, height=600 )

    summary_df.to_csv(f"./results/{name}mutations_ont_summary.csv")


