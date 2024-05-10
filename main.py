import openai
from dotenv import load_dotenv
import os
import PyPDF2
# import fitz

class ExpertTranslator():

    def __init__(self, pdf_file_name, is_save_original_text, is_save_translation, model_name, api_key):
        
            self.pdf_file_name = pdf_file_name
            self.is_save_original_text = is_save_original_text
            self.is_save_translation = is_save_translation

            # Define a proper system message for our use case
            agent = f"""
            Propose: You are an AI designed to translate articles from portuguese brazil to english. 
            Method: The text will come in chunks and you will only answer with the translation done that must maintain the technical terms and coherence.
            """

            # Initialize your model's memory
            self.message_history = [{'role': 'system', 'content': agent}]
            self.model_name = model_name
            self.translation = None
            self.client = openai.OpenAI(api_key=api_key)

    def extract_text_from_pdf(self, pdf_file_name):

        #doc = fitz.open(stream=pdf_file_name.read(), filetype="pdf")
        doc = PyPDF2.PdfReader(pdf_file_name)

        # print the number of pages in pdf file
        # print(len(doc.pages))

        # # print the text of the first page
        # print(doc.pages[0].extract_text())
        
        text = ""
        for page in doc.pages:
            text += page.extract_text()
            
        return text

    def gpt_agent(self, prompt):


        len_message_history = len(self.message_history)

        if len_message_history == 9:
            #print("\n\n#ANTES:\n", self.message_history)
            final_index = int(len_message_history/2)
            self.message_history[1:final_index] = self.message_history[final_index+1:]
            self.message_history[final_index+1:] = []
            
            if len_message_history%2 == 0:
                self.message_history.pop()
            #print("\n\n#DEPOIS:\n", self.message_history)
            #return 0
                
        if len_message_history == 1:
            self.message_history.append({'role': 'user', 'content': prompt})
        else:
            content = f"""
                the last translation was {self.message_history[-1]['content']}.
                now continue translating this: {prompt}
            """
            self.message_history.append({'role': 'user', 'content': content})

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=self.message_history
        )

        response_text = response.choices[0].message.content
        self.message_history.append({'role': 'assistant', 'content': response_text})
        
        return response_text
    
    def save_original_text(self, text):
        with open("text_original.txt", "w") as text_file:
            text_file.write(text)

    def create_chunks(self, text, step):

        chunks = list()

        for i in range(1, len(text), step):

            chunk = text[i:i+step]
            chunks.append(chunk)

        return chunks

    def concat_string(self, list_text):
        
        text = ""

        for elem in list_text:
            text += elem

        return text

    def save_translation(self, answers):
        
        text = self.concat_string(answers)

        with open("traducao.txt", "w") as text_file:
            text_file.write(text)

    def get_translation(self):

        return self.translation
    
    def set_translation(self, list_text):
        
        text = self.concat_string(list_text)
        self.translation = text

    def start(self):
         
        text = self.extract_text_from_pdf(self.pdf_file_name)
        print(print('# text len', len(text)))

        if self.is_save_original_text:
            self.save_original_text(text)

        #Answer the same question for each chunk
        answers = list()

        chunks = self.create_chunks(text, step=700)
        print('# chucks', len(chunks))
        print('# chuck', len(chunks[0]))

        for chunk in chunks:
            
            answer = self.gpt_agent(chunk)
            # if answer == 0:
            #     break
#            print('\n\n# answer', answer)
            answers.append(answer)

        self.set_translation(answers)

        if self.is_save_translation:
            self.save_translation(answers)



if __name__ == '__main__':

    load_dotenv()

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    pdf_file_name = "RedesLoRaWAN.pdf"

    is_save_original_text = True
    is_save_translation = True
    model_name = "gpt-3.5-turbo-1106"
    # model = "gpt-4"

    if pdf_file_name is not None:
        expert_translator = ExpertTranslator(pdf_file_name, is_save_original_text, is_save_translation, model_name, OPENAI_API_KEY)

        expert_translator.start()
        translation = expert_translator.get_translation()

#dificuldade com o limite de token dado pelo model_name
#nao esta extraindo palavras com acentos corretamente
#melhorar a formatação do texto        