import streamlit as st
import pandas as pd
from sklearn.preprocessing import LabelEncoder
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

st.markdown('### Whatsapp Explorer Data Analysis')
csv_file_path = "reports/Report-181023.csv"
if csv_file_path is not None:
    df = pd.read_csv(csv_file_path)
    df['DOJ'] = pd.to_datetime(df['DOJ'])
    df['DOJ'] = df['DOJ'].dt.strftime('%m/%d/%y')
    df['DOJ'] = pd.to_datetime(df['DOJ']) 
    
    # st.write(type(df["DOJ"].iloc[0]))

   # Get the minimum and maximum dates from the 'DOJ' column
    min_doj = df['DOJ'].min()
    max_doj = df['DOJ'].max()
    # st.write(type(min_doj), max_doj)
    # Add date range selectors for Date of Joining (DOJ)
    doj_start = st.date_input('Select Start Date for Date of Joining (DOJ)', min_doj)
    doj_end = st.date_input('Select End Date for Date of Joining (DOJ)', max_doj)
    st.write(doj_start, doj_end)
    doj_start = pd.to_datetime(doj_start)
    doj_end = pd.to_datetime(doj_end)
    

    
    st.write("Latest Report:")
    st.write(df)

    st.markdown('### Filter and Analyze Data')

    age_range = st.slider('Select Age Range:', min_value=int(df['Age'].min()), max_value=int(df['Age'].max()), value=(int(df['Age'].min()), int(df['Age'].max())))
    all_caste = st.checkbox('Select All Castes')
    caste_options = df['Caste'].unique() if all_caste else st.multiselect('Select Caste:', df['Caste'].unique())
    all_religion = st.checkbox('Select All Religions')
    religion_options = df['Religion'].unique() if all_religion else st.multiselect('Select Religion:', df['Religion'].unique())

    # Apply dynamic filters to the data
    filtered_data = df[
        (df['Age'] >= age_range[0]) & (df['Age'] <= age_range[1]) &
        (df['Caste'].isin(caste_options)) &
        (df['Religion'].isin(religion_options)) &
        (df['DOJ'] >= doj_start) & (df['DOJ'] <= doj_end)
    ]
    
    data_dropped_na = filtered_data.dropna(subset=['Age', 'Caste', 'Religion', 'Consented Groups'])
    

    # Display the filtered data
    st.write("Filtered Data:")
    st.write(filtered_data)
    
    availableMetrics = ["Descriptive Statistics", "Correlation Matrix" , "Average Groups Donated by Age", "Average Groups Donated by Religion and Caste", "Political Inclination"]
    selectedOption = st.selectbox('Select Metric', availableMetrics)
    

    if (selectedOption == "Descriptive Statistics"):
        # Calculate descriptive statistics for numerical variables
        descriptive_stats = filtered_data.describe()

        # Show descriptive statistics
        st.write(descriptive_stats)
    elif (selectedOption == "Correlation Matrix"):
        

        # Drop rows with missing values in relevant columns for accurate correlation

        # Encode the 'Caste' and 'Religion' columns
        label_encoder = LabelEncoder()
        data_dropped_na['Caste_encoded'] = label_encoder.fit_transform(data_dropped_na['Caste'])
        data_dropped_na['Religion_encoded'] = label_encoder.fit_transform(data_dropped_na['Religion'])

        # Calculate correlation matrix for 'Age', 'Caste_encoded', 'Religion_encoded', and 'Consented Groups'
        correlation_matrix = data_dropped_na[['Age', 'Caste_encoded', 'Religion_encoded', 'Consented Groups']].corr()

        # Show correlation matrix
        st.write(correlation_matrix)

    elif (selectedOption == "Average Groups Donated by Age"):
        # Create age buckets
        bins = [0, 20, 30, 40, 50, 100]
        labels = ['0-20', '21-30', '31-40', '41-50', '51+']
        data_dropped_na['Age_Bucket'] = pd.cut(data_dropped_na['Age'], bins=bins, labels=labels, right=False)

        # Compute the average number of groups consented by age bucket
        avg_consent_by_age_bucket = data_dropped_na.groupby('Age_Bucket')['Consented Groups'].mean().reset_index()

        st.write(avg_consent_by_age_bucket)

        # Calculate the size of each age bucket
        bucket_size = data_dropped_na['Age_Bucket'].value_counts().reset_index()
        bucket_size.columns = ['Age_Bucket', 'Size']
        # Generate new x-axis labels with bucket size included
        new_labels = [f"{label} (n={size})" for label, size in zip(bucket_size.sort_values('Age_Bucket')['Age_Bucket'], bucket_size.sort_values('Age_Bucket')['Size'])]

        # Create the bar plot with 95% confidence intervals
        plt.figure(figsize=(12, 6))
        sns.barplot(x='Age_Bucket', y='Consented Groups', data=data_dropped_na, order=labels, capsize=0.1, ci=95)
        plt.title('Bar Plot of Average Consented Groups by Age Bucket with 95% CI')
        plt.xlabel('Age Bucket')
        plt.ylabel('Average Consented Groups')
        plt.xticks(ticks=range(len(new_labels)), labels=new_labels)
        fig = plt.gcf()
        st.pyplot(fig, use_container_width=True)
        # st.plotly_chart(plt, use_container_width=True)

    elif (selectedOption == "Average Groups Donated by Religion and Caste"):
        caste_translation = {
            'ओ.बी.सी (अन्य पिछड़ा वर्ग)': 'OBC (Other Backward Class)',
            'दलित/अनुसूचित जाति': 'Dalit/Scheduled Caste',
            'जनरल/उच्च': 'General/Upper',
            'अनुसूचित जनजाति': 'Scheduled Tribe'
        }

        religion_translation = {
            'हिन्दू धर्म': 'Hinduism',
            'इस्लाम': 'Islam',
            'ईसाई धर्म': 'Christianity'
        }

        # Translate the 'Caste' and 'Religion' columns
        data_dropped_na['Caste_English'] = data_dropped_na['Caste'].map(caste_translation)
        data_dropped_na['Religion_English'] = data_dropped_na['Religion'].map(religion_translation)

        # Create separate bar plots for 'Caste_English' and 'Religion_English' against 'Consented Groups' with 95% CI

        # Bar plot for 'Caste_English'
        plt.figure(figsize=(10, 6))
        sns.barplot(x='Caste_English', y='Consented Groups', data=data_dropped_na, capsize=0.1, ci=95)
        plt.title('Bar Plot of Average Consented Groups by Caste with 95% CI')
        plt.xticks(rotation=90)
        plt.xlabel('Caste (English)')
        plt.ylabel('Average Consented Groups')
        fig1 = plt.gcf()

        # Bar plot for 'Religion_English'
        plt.figure(figsize=(10, 6))
        sns.barplot(x='Religion_English', y='Consented Groups', data=data_dropped_na, capsize=0.1, ci=95)
        plt.title('Bar Plot of Average Consented Groups by Religion with 95% CI')
        plt.xticks(rotation=90)
        plt.xlabel('Religion (English)')
        plt.ylabel('Average Consented Groups')
        fig2 = plt.gcf()
        
        st.pyplot(fig1, use_container_width=True)
        st.pyplot(fig2, use_container_width=True)
    
    elif (selectedOption == "Political Inclination"):
        political_parties = ['INC', 'ApnaDal', 'SP', 'RLD', 'BJP', 'BSP']
        # age_bins = [20, 30, 40, 50, 60, 70]
        filtered_data_with_political_responses = data_dropped_na[data_dropped_na[political_parties].notna().any(axis=1)]
        # if not filtered_data_with_political_responses.empty:
        #     st.header("Inclination Towards Political Parties")  

        #     # List of political parties
        #     parties = ['INC', 'ApnaDal', 'SP', 'RLD', 'BJP', 'BSP']

        #     # Create a separate plot for each political party
        #     for party in parties:
                
        #         st.subheader(f'Inclination Towards {party}')
        #         plt.figure(figsize=(10, 6))
        #         plt.title(f'Inclination Towards {party}')
                
        #         # Convert numerical values to strings for the plot labels or data
        #         filtered_data['Age'] = filtered_data['Age'].astype(str)
        #         filtered_data[party] = filtered_data[party].astype(str)
                
        #         filtered_data.plot.scatter(x='Age', y=party, c='red', colormap='viridis', s=filtered_data[party].astype(float) * 50, alpha=0.5, edgecolors="k", legend=True)
        #         plt.xlabel('Age')
        #         plt.ylabel(f'Inclination Towards {party}')
        #         st.pyplot(plt)
        # else:
        #     st.warning("No filtered data available for visualization.")
    
        age_bins = [20, 30, 40, 50, 60, 70]
        # Create a dictionary to map values to labels
        mapping = {2: 'Very Inclined', 1: 'Inclined', -1: 'Far', -2: 'Very Far'}


        # Group data by age buckets
        filtered_data_with_political_responses['Age Group'] = pd.cut(filtered_data_with_political_responses['Age'], bins=age_bins)

       # Create a separate scatter plot for each political party
        political_parties = ['INC', 'ApnaDal', 'SP', 'RLD', 'BJP', 'BSP']

        st.header("Inclination Towards Political Parties")

        for party in political_parties:
            st.subheader(f'Inclination Towards {party}')
            plt.figure(figsize=(10, 6))
            plt.title(f'Inclination Towards {party}')
            
            # Map values to labels for plotting
            data_dropped_na['Inclination'] = data_dropped_na[party].map(mapping)
            
            # Count the number of participants for each inclination
            inclination_counts = data_dropped_na['Inclination'].value_counts().reindex(mapping.values(), fill_value=0)
            
            # Plot a bar chart
            inclination_counts.plot(kind='bar', colormap='viridis', ax=plt.gca())
            
            plt.xlabel('Inclination')
            plt.ylabel('Number of Participants')
            
            # # Show mapping information in the plot
            # st.text("Mapping:")
            # st.text(mapping)
            
            # Show the scatter plot
            st.pyplot(plt)

        
        





