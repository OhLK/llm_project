import os


def create_book(directory, output_filename):
    """Combina arquivos Markdown em um único arquivo tipo livro."""

    with open(output_filename, "w", encoding="utf-8") as outfile:
        outfile.write("# Bíblia de Engenharia de Dados\n\n")  # Título principal

        for filename in sorted(
            os.listdir(directory)
        ):  # Ordena os arquivos para manter a ordem dos capítulos
            if filename.endswith(".md"):
                filepath = os.path.join(directory, filename)
                with open(filepath, "r", encoding="utf-8") as infile:
                    content = infile.read()

                    # Extrai o título do capítulo (nível h1)
                    lines = content.splitlines()
                    chapter_title = ""
                    for line in lines:
                        if line.startswith("# "):
                            chapter_title = line.lstrip("# ").strip()
                            break

                    if (
                        not chapter_title
                    ):  # Define um título padrão se não encontrar um h1
                        chapter_title = filename.replace(".md", "")

                    outfile.write(
                        f"## {chapter_title}\n\n"
                    )  # Título do capítulo (nível h2)
                    outfile.write(content)
                    outfile.write("\n\n")  # Adiciona espaço entre os capítulos


if __name__ == "__main__":
    directory = "summaries"  # Nome da pasta com os arquivos .md
    output_filename = "Bíblia_de_Engenharia_de_dados.md"
    create_book(directory, output_filename)
    print(f"Livro criado com sucesso: {output_filename}")
