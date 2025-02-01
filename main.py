import requests
from bs4 import BeautifulSoup
import csv
import os
from langchain.schema import SystemMessage, HumanMessage
from langchain_google_genai import GoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")


def get_website_content(url):
    """
    Obtém o conteúdo de um website com User-Agent modificado.
    Retorna o conteúdo textual das tags <p> da página.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Gera um erro para status codes HTTP ruins

        soup = BeautifulSoup(response.content, "html.parser")
        text_content = " ".join([p.get_text() for p in soup.find_all("p")])

        return text_content
    except requests.exceptions.RequestException as e:
        print(f"Erro ao acessar {url}: {e}")
        return ""


def filter_links_by_label(csv_file, label):
    """
    Filtra os links de um arquivo CSV com base na categoria (label).
    Retorna uma lista de links associados à label especificada.
    """
    links = []
    with open(csv_file, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["label"] == label:
                links.append(row["link"])
    return links


def create_directory(directory_name):
    """
    Cria um diretório se ele não existir.
    """
    if not os.path.exists(directory_name):
        os.makedirs(directory_name)


def generate_summary(text, model):
    """
    Gera um resumo educacional do texto fornecido usando um LLM.
    """
    try:
        messages = [
            SystemMessage(
                content="Você é um assistente prestativo especializado em criar resumos academicos detalhados e informativos.",
            ),
            HumanMessage(
                content=f"""
                    Explicar os principais conceitos, teorias e argumentos apresentados no texto de forma clara e objetiva.
                    Identificar e definir os termos técnicos mais importantes, fornecendo exemplos concretos para ilustrar cada um deles.
                    Organizar as informações de forma lógica e coerente, utilizando subtítulos para melhorar a legibilidade.
                    Destacar as implicações práticas dos conceitos discutidos no texto.
                    Incluir uma breve introdução e uma conclusão.Após o resumo, crie um tutorial prático, em formato de guia passo a passo, que ensine como aplicar os conceitos do texto. O tutorial deve ser adequado para o mesmo público do resumo (estudantes universitários de ciência da computação do primeiro ano) e deve incluir exemplos de código funcionais e explicações detalhadas de cada etapa.
                    O resumo deve conter ao menos 800 palvras
                    Após o resumo, crie um tutorial prático, em formato de guia passo a passo, O tutorial deve ser adequado para o mesmo público do resumo (estudantes universitários de ciência da computação do primeiro ano) e deve incluir exemplos de código funcionais e explicações detalhadas de cada etapa.

                    {text}

                    Devolva em markdown
                    """
            ),
        ]

        llm = GoogleGenerativeAI(
            model=model, max_tokens=8000, temperature=0.2, google_api_key=API_KEY
        )
        response = llm.invoke(messages)

        return response
    except Exception as e:
        print(f"Erro ao gerar resumo com o LangChain: {e}")
        return ""


csv_file = "data.csv"
# liste os labels
labels = set()
with open(csv_file, "r", encoding="utf-8") as file:
    reader = csv.DictReader(file)
    for row in reader:
        labels.add(row["label"])

labels

# data distribution of the labels
label_counts = {label: 0 for label in labels}
with open(csv_file, "r", encoding="utf-8") as file:
    reader = csv.DictReader(file)
    for row in reader:
        label_counts[row["label"]] += 1

label_counts


def main():
    """
    Função principal que orquestra o processo de coleta de conteúdo, agrupamento por label e geração de resumos.
    """
    csv_file = "data.csv"  # Substitua pelo caminho do seu arquivo CSV
    target_label = input("Digite a categoria (label) que deseja filtrar: ")

    summaries_dir = "summaries"
    create_directory(summaries_dir)

    filtered_links = filter_links_by_label(csv_file, target_label)

    if not filtered_links:
        print(f"Nenhum link encontrado para a categoria '{target_label}'.")
        return

    model = "gemini-exp-1206"

    all_content = ""
    for link in filtered_links:
        print(f"Processando: {link}")
        website_content = get_website_content(link)
        if website_content:
            all_content += website_content + " "

    if all_content:
        summary = generate_summary(all_content, model=model)

        filename = os.path.join(summaries_dir, f"resumo_{target_label}.md")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"Resumo gerado para a categoria: {target_label}\n\n")
            f.write(summary)
        print(f"Resumo salvo em: {filename}")
    else:
        print(f"Não foi possível gerar resumo para a categoria: {target_label}")


if __name__ == "__main__":
    main()
