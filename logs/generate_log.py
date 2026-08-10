import pandas as pd

columns = ["QuestionID", "UserID", "Timestamp", "Question", "Chunks", "Answer", "Runtime", "Total_Tokens", "Prompt_Tokens",  "Completion_Tokens", "Successful_Requests", "Agent1_Output", "Agent2_Output", "Agent3_Output", "Agent5_Output", "Verifier_Agent_Runs"]

df = pd.DataFrame(columns = columns)

df.to_excel("log.xlsx", columns = columns, index = False)