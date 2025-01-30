from langchain_community.llms import Ollama


class Chatbot:
    def __init__(self):
        self.ollama = Ollama(model="mwiewior/bielik", base_url="http://localhost:11434")
        self.prompt = " "

    def describe_table(self, df_table):
        self._get_prompt(df_table)
        response = self.ollama.invoke(self.prompt)
        return response

    def _get_prompt(self, df_table):
        self.prompt = f"""
        Here is a table of the top 5 locations determined by an algorithm:

        {df_table}      

        The 'Algorytm' represents the overall ranking, and the other features are the attributes that 
        influenced the score. The 'Przestępstwa' and 'Zanieczyszczenie Powietrza' should be as low as possible.
        Rest of features should be high. The 'Połączenia lotnicze', 'Liczba Portów Lotniczych', 
        'Pobliskie Linie Kolejowe', 'Pogoda' and 'Liczba Przystanków Autobusowych' should be as high as possible.
        
        Explain why these locations have high scores based on the provided data. If the UNESCO_list is not empty
         - tell few words about the UNESCO objects in this region. Don't mention specific values like 0.798. 
         Write in polish.

        """


