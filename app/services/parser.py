import sys
import json

def read_text_file(filename):
    try:
        with open(filename, "r" , encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        print(f"Error: file {filename} not found.")
        return None
    

def analyze_file(text):
    text_lower = text.lower()
    words = text.split()
    
    project_type = "unknown"
    if "residential" in text_lower:
        project_type = "residential"
    elif "commercial" in text_lower:
        project_type = "commercial"
    
    area_mention = []
    for i, word in enumerate(words):
        if "sqft" in word or "sqm" in word:
            if i>0:
                area_mention.append(words[i-1] + " " + word)
    
    budget_mention = []
    for i,word in enumerate(words):
        if "usd" in word or "million" in word:
            if i > 0:
                budget_mention.append(words[i-1] + " " + word)
    
    return{
        "project_type" : project_type,
        "area_mention" : area_mention,
        "budget_mention" : budget_mention,
        "raw_text_length" : len(text)
    }

def save_output(data,output_file = "output.json"):
    with open(output_file,"w" , encoding="utf-8") as file:
        json.dump(data,file,indent = 4)

def main():
    if len(sys.argv) < 2:
        print("Usage: python document_parser.py <input_file>")
        return
    
    input_file = sys.argv[1]


    text = read_text_file(input_file)
    if text is None:
        return 
    

    result = analyze_file(text)
    save_output(result)

    print(f"Analysis complete for '{input_file}', output written to output.json ")



if __name__ == "__main__":
    main()




