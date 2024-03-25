from pandasai.llm import GoogleVertexAI
from pandasai import Agent
import pandas as pd
from pandasai.llm import OpenAI
import warnings


# Ignore warnings on Gemini
warnings.filterwarnings("ignore", "Your application has authenticated using end user credentials")


## Use openai, gpt-4 is way better and suited for this job imo
# llm = OpenAI(model="gpt-4", api_token="")

# Use gemini
llm = GoogleVertexAI(project_id="",
                    location="us-central1",
                     model="gemini-pro")

# Load the hayabusa security logs, change this to your own logs
events = pd.read_csv("sample_logs.csv")

# Add agent with system prompt
agent = Agent(events, description="""
I am analyzing security logs from Hayabusa to assist security analysts in identifying potential security incidents without manually going through each log entry. Given the logs with the following important columns, I will provide insights and highlight the crucial information for quick decision-making:

If you were asked to summarize, just summarize it based on your knowledge and the logs given.
Usually for open ended questions, you can ask me to reply just in text. Code is only for dataframe (really specific questions), and image only for charts.
              
1. **Timestamp**: The date and time when the event was logged. It helps in identifying when the incident occurred.
2. **RuleTitle**: The name of the rule that triggered the event. It provides context on what kind of security policy was violated or which security check was triggered.
3. **Level**: The severity level of the event (e.g., Information, Warning, Critical). It helps in prioritizing the events that require immediate attention.
4. **Computer**: The name or IP address of the computer where the event occurred. This information is crucial for pinpointing the source of a potential security breach.
5. **Channel**: The part of the system where the event was logged (e.g., System, Application, Security). It aids in categorizing the event.
6. **EventID**: A unique identifier for the type of event. This helps in classifying the event and searching for more information or similar events.
7. **RecordID**: A unique identifier for the specific log entry. It is useful for referencing and tracking individual events.
8. **Details**: A detailed description of the event. This field provides the most context about what happened, including any specific messages or error codes.
9. **ExtraFieldInfo**: Any additional information that can provide more context to the event. It might include user names, network information, or other relevant data not captured in the other fields.
""",
config={"llm": llm, "custom_whitelisted_dependencies": ["re"], "save_charts": True, "enforce_privacy": True})



while True:

    try:
        user_input = input("\033[94mEnter your request or type 'exit' to quit: \033[0m")
        
        # Check for exit condition
        if user_input.lower() == 'exit':
            print("\033[91mExiting. Goodbye!\033[0m")
            break

        response = agent.chat(user_input)

        # Process the response based on its type

        # If it returns a number
        if isinstance(response, int):
            print(f"\033[92m{response}\033[0m")

        # If it returns a dataframe
        elif isinstance(response, pd.DataFrame):
            if (response.shape[0] == 0):
                print("\033[91mNo records found.\033[0m")
                continue
            print(f"\033[93mWe found {len(response)} records. What file name do you want to save it?\033[0m")
            file_name = input("\033[94mEnter the .csv file name: \033[0m")
            file_location = "./output_records/" + file_name + ".csv"

            response.to_csv(file_location, index_label='Index')
            print(f"\033[92mOutput saved to {file_location}\033[0m")  

        # If it returns a chart
        elif (response.endswith(".png")):
            print(f"\033[92mYour image has been saved at \n{response}\033[0m")

        else:
            # For text or other response types, just print the response.
            print(f"\033[96m{response}\033[0m")

    except Exception as e:
        print(f"\033[91mAn error occurred: {str(e)}\033[0m")