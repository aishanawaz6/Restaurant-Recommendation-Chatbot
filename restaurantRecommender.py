# Description: 
# The task involves developing a chatbot that assists users in finding suitable restaurants based on their preferences. 
# The chatbot should be able to understand user queries & provide relevant recommendations.
# The chatbot should support the following functionalities:

# -> Accept user input regarding location, cuisine preferences, and budget constraints.
# -> Ask for additional clarification if required.
# -> Retrieve and display a list of restaurants that match the user's preferences.
# -> Allow users to filter the results based on specific criteria (e.g., ratings, price range, distance).
# -> Provide details such as restaurant names, addresses, contact information, and user ratings for each recommendation.
# -> Handle user feedback and improve recommendations over time.

# Data: To train the chatbot, you will need a dataset containing information about restaurants. This dataset should include:
# Restaurant names, Addresses, Contact information (phone numbers, websites), Cuisine types, Price ranges, Ratings & reviews
# You can gather this data from various sources, such as online restaurant directories or review websites. 
# Make sure to respect data usage rights and obtain the necessary permissions when collecting the data.

# Guide to Solution: To implement the chatbot, you can follow these steps:

# Step 1: Data Collection and Preprocessing : 
# Gather the restaurant data from reliable sources and ensure it is in a structured format.

#DATA GATHERED FROM : https://www.kaggle.com/datasets/mikhailpustovalov/scraped-data-from-ta
import pandas as pd
resData=pd.read_csv('dataset.csv')
resData=resData[['name','address','tel','cuisines','pricing','rating','reviews']]

# Preprocess the data by cleaning and normalizing it (e.g., removing duplicates, standardizing addresses).
resData.isnull().sum()
resData.dropna(inplace=True)           #REMOVING MISSING VALUES
resData.drop_duplicates(inplace=True)  #REMOVING DUPLICATES
resData=resData[0:8000]                #Restricting the valid enteries to 8,000 because Jupyter Freezes with any larger size
resData.head()

resData.info()

resData.describe()

# Step 2: Natural Language Processing (NLP)
# Implement a natural language understanding module to extract key information from user queries, 
# such as location, cuisine preferences, and budget constraints.
# Use techniques like named entity recognition and part-of-speech tagging to identify 
# relevant entities and extract their values.

import spacy
from nltk import word_tokenize

def naturalLanguageUnderstandingModule(userInput,backendVisible=False):
    
    if(backendVisible): #FOR Testing purposes
        print("\nUser Input is:",userInput)
        print('\nNatural Language Understanding Module Running (In Backend Visible Mode)..')
    
    
    tokens = word_tokenize(userInput)   # Tokenizing the input
    nlp = spacy.load("en_core_web_sm")  # Loading the spaCy English model
   
    # Extracting relevant entities           [ENTITY RECOGNITION]
    relevantEntities = []
    for ent in nlp(userInput).ents:
        if ent.label_ in ["GPE", "LOC"]:         # Location entities
            relevantEntities.append(("Location", ent.text))
        elif ent.label_ == "MONEY":             # Budget entities
            relevantEntities.append(("Budget", ent.text))
    
    # Defining common cuisine keywords
    cuisineKeywords = list(resData['cuisines'].values)
    
    # Extracting cuisine preferences using keyword matching method
    cuisinePREF = []
    for token in tokens:
        for tokens2 in cuisineKeywords:
            tokens3=str(tokens2).split(",") #This is to cater list of lists
            for token4 in tokens3:
                token=token.replace(" ","") #Removing spaces
                token4=token4.replace(" ","")
                if token.lower() == token4.lower():
                    cuisinePREF.append(token)
                    
    result=[]
        
    if(backendVisible):  #FOR Testing purposes, Printing the extracted information:
        print("\nExtracted Information-->\n")
        
    for Type, Value in relevantEntities:
        if(backendVisible):  #FOR Testing purposes
            print(Type,":",Value)
        result.append(Value)
        
    cuisinePREF=list(dict.fromkeys(cuisinePREF)) #Removing duplicates
    cuisinePREF=' '.join(cuisinePREF)            #Converting to String
    result.append(cuisinePREF)
        
    if(backendVisible):  #FOR Testing purposes
        print("Cuisine Preferences:",cuisinePREF,'\n')

    return result

# Example Input
inp="Find restaurants in England with a budget of $50 per person & Mediterranean food"

# naturalLanguageUnderstandingModule(inp,False) #Pass false to hide backend working
naturalLanguageUnderstandingModule(inp,True)    #Pass true to see how backend works

# Step 3: Recommendation System
# Develop a recommendation system that takes the extracted user preferences as input and retrieves relevant restaurants
# from the dataset. Consider using techniques like content-based filtering 
# or collaborative filtering to generate personalized recommendations based on user preferences & past interactions.

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from IPython.display import display
from colorama import Fore, Back, Style
from timeit import default_timer as timer

# Creating a combined feature for recommendation using relevant columns
resData['features'] = resData['cuisines'] + ' ' + resData['pricing'] +' '+ resData['address']+' ' + resData['rating']
resData.reset_index(drop=True, inplace=True)

# Vectorizing the combined features
vectorizer = TfidfVectorizer(stop_words='english')
tfidfMatrix = vectorizer.fit_transform(resData['features'])

# Computing similarity scores
cosineSimilarities = cosine_similarity(tfidfMatrix)

# Returns Top N Recommendations based on user preferences (By default 3)
def RecommendationsGETTER(preferences,topN=3):
    
    # Filtering the restaurants that match the user preferences
    matchingRes = resData[resData['cuisines'].apply(lambda x: any(pref.lower() in x.lower() for pref in preferences))]
    
    if len(matchingRes) == 0:
        return "No matching restaurants found."
    
    # Calculating the average similarity scores for all matching restaurants:
    avgSimilarities = np.nanmean(cosineSimilarities[matchingRes.index], axis=0)
    avgSimilarities[np.isnan(avgSimilarities)] = 0   # Replacing NaN values with 0
    

    topI = avgSimilarities.argsort()[:-topN-1:-1]   # Saving indices of top N recommended restaurants
    recommendations = resData.iloc[topI]            # Storing Recommended Restaurants FULL Details

    return recommendations

def getRecommendations(pref,n): #Like wrapper fuction
    
    start = timer()
    recommendations = RecommendationsGETTER(userPREF,n)
    end=timer()
    
    timeTaken=round(end-start,4)   #As most search engines have time taken calculation
    
    #CHECKING if any matching restaurants found:
    if isinstance(recommendations, str):
        print(recommendations)
        return 'None'
    else:
        print(Fore.RED+"\n  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Showing Top",n,"Recommended Restaurants Results (in",timeTaken,"seconds) ~~~~~~~~~~~~~~~~~~~~~~")
        display(recommendations)
        return recommendations
        

        
        
# Example PAST user preference 
userPREF = ['European','Paris']
#Getting top 5 Recommendations based on PAST user preference
reco=getRecommendations(userPREF,5)

# Step 4: User Interface and Interaction
# Design a user interface for the chatbot, allowing users to input their preferences & view the recommended restaurants.
# Implement a conversational flow that guides users through the interaction, asking for clarification when necessary.
# Define the conversational flow
from colorama import Fore, Back, Style

def userInterface():
    i=1
    name=input("Name? ")
    print(Back.RED)
    print(Fore.WHITE+"\n\n~~~~~~~~~~~ Welcome to the GlowingSoft Technologies's Restaurant Recommendation Chatbot",name,"! ~~~~~~~~~~~~")
    print('\nYou may enter exit anytime to end')
    
    while(True):
        #First User inputs preferences
        preferences = input("\n                                               How may I help you? \n\n") 
        if(preferences.lower() in 'exit'):
            print(Fore.WHITE)
            print(Back.BLUE+'Thank You for using our Chatbot!')
            break
            
        print(Fore.WHITE)
        print(Back.BLUE)
        preferences=naturalLanguageUnderstandingModule(preferences)   #NLP
       
        print(Style.RESET_ALL)
        
        while(True): #Like do while loop to handle user input errors
            n=input("How many recommendations do you wish to receive? ") #Asking for more clarification
            if(not(n.isnumeric())):
                print('\nERROR! Invalid Input. Enter a number')
            elif(int(n)>0 and int(n)<=800):
                break
            elif(int(n)==0):
                print('\nERROR! Please enter a valid number above 0!')
            elif(int(n)>800):
                print('\nERROR! System can handle maximum 800 best matching recommendations.') #800 set after several testing
            else:
                print('\nERROR! Invalid Input. Try Again')
                
        
        print('\nGetting your recommendations...')    
        reco=getRecommendations(preferences,int(n))             #Generates & Displays Recommendations accordingly
        
        if(not(isinstance(reco, str))):#If any recommendations were received
            while (True): #TO SAVE RECOMMENDATIONS GIVEN BY SYSTEM
                save=input('\nWould you like to save your recommendations in excel file for future use? (yes/no) ')
                if(save.lower() in 'yes'):
                    nameFile='userRecommendations'+str(i)+'.xlsx'
                    reco.to_excel(nameFile)
                    print('\nRecommendations saved to file named',nameFile)
                    break
                elif(save.lower() in 'no'):
                    print('\nYour Recommendations won\'t be saved')
                    break
                else:
                    print('\nERROR! Invalid Input. Try Again')
        
        i=i+1 #For naming file purposes so each recommendation is saved in a different file

userInterface()

# Step 5: Evaluation and Iteration
# Test the chatbot with a variety of user queries & evaluate its performance.
# Incorporate user feedback and continuously improve the chatbot's recommendation accuracy and user experience.
# Remember to document each step of the development process and perform thorough testing to ensure
# the chatbot's reliability and effectiveness.

#IN SEPEARATE DOCUMENT 
