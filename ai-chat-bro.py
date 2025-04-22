import argparse, os
from ollama import Client
import readline

ollama = Client()

def read_code(file_path):
    with open(file_path, 'r') as f:
        return f.read()

def start_chat(file_path, code, project_name):
    print(f"\n📄 File: {file_path}")
    print("🧠 AI Coding Assistant (LLaMA 3) Ready...")

    messages = [
        {"role": "system", "content": "You are a senior full-stack developer who helps with improving, debugging, and suggesting best practices."},
        {"role": "user", "content": f"Here is a code file from project '{project_name}':\n\n{code}"},
        {"role": "user", "content": "Ask me what I'm trying to build and provide guidance or suggestions."}
    ]

    response = ollama.chat(model='llama3', messages=messages)
    print(f"\n🤖 {response['message']['content']}")
    messages.append(response['message'])

    while True:
        try:
            user_input = input("\n👨 You: ")
            messages.append({"role": "user", "content": user_input})

            response = ollama.chat(model='llama3', messages=messages)
            print(f"\n🤖 {response['message']['content']}")
            messages.append(response['message'])

        except KeyboardInterrupt:
            print("\n👋 Exiting chat.")
            break

def handle_file(file_path):
    project_name = os.path.basename(os.path.dirname(file_path))
    code = read_code(file_path)
    start_chat(file_path, code, project_name)

def handle_folder(folder_path):
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".py"):
                full_path = os.path.join(root, file)
                handle_file(full_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Coding Assistant CLI")
    parser.add_argument("--file", help="Analyze a specific Python file")
    parser.add_argument("--folder", help="Analyze all Python files in a folder")

    args = parser.parse_args()

    if args.file:
        handle_file(args.file)
    elif args.folder:
        handle_folder(args.folder)
    else:
        print("❗ Please use --file or --folder")
