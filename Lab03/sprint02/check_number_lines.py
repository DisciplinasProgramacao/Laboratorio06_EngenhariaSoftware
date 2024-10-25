import os
import csv

def count_csv_lines(csv_file_path):
    with open(csv_file_path, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)
        line_count = sum(1 for _ in reader)
    return line_count

def check_csv_files_in_folder(folder_path, expected_line_count=100):
    files_with_incorrect_lines = []
    
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.csv'):
            csv_file_path = os.path.join(folder_path, file_name)
            line_count = count_csv_lines(csv_file_path)
            
            if line_count != expected_line_count:
                files_with_incorrect_lines.append((file_name, line_count))
    
    return files_with_incorrect_lines

def main():
    folder_path = './results'
    files_with_issues = check_csv_files_in_folder(folder_path)
    
    if files_with_issues:
        print("Os seguintes arquivos não possuem 100 linhas (excluindo o cabeçalho):")
        for file_name, line_count in files_with_issues:
            print(f'{file_name}: {line_count} linhas')
    else:
        print("Todos os arquivos possuem 100 linhas.")

if __name__ == '__main__':
    main()
