from pandas import DataFrame
from seedir import seedir


def format_dataframe(dataframe: DataFrame, header: str) -> str:
    return "\n".join([f"{header}\t{dataframe.index[i]}\n{dataframe.iloc[i].to_string()}\n"
                      for i in range(len(dataframe))])


def format_list(input_list: list) -> str:
    return "\n".join(input_list)


def format_directory_tree(directory_path: str) -> str:
    return str(seedir(path=directory_path, style='lines', printout=False, depthlimit=4))


def create_text_file(path: str, content: str) -> str:
    with open(path, "w+") as file:
        file.write(content)
        return file.name
