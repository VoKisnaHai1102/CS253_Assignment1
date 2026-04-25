#include <iostream>
#include <fstream>
#include <string>
#include <unordered_map>
#include <vector>
#include <queue>
#include <cctype>
#include <algorithm>
#include <stdexcept>
#include <chrono>
#include <memory>
#include <cstring>
using namespace std;
using namespace std::chrono;

template <typename T>
void printTopKQueue(priority_queue<T, vector<T>, greater<T>>& pq) {
    vector<T> results;
    while (!pq.empty()) {
        results.push_back(pq.top());
        pq.pop();
    }
    // the first element in the vector is the most frequent word, so we print in reverse order
    for (auto it = results.rbegin(); it != results.rend(); ++it) {
        cout << it->second << " -> " << it->first << "\n";
    }
}


class BufferedFileReader {
private:
    ifstream file;
    size_t bufferSize;
    char* buffer;
    string leftover; // for handling tokens split across chunks 

public:
    BufferedFileReader(const string& filename, size_t bufferKb) {
        bufferSize = bufferKb * 1024;
        buffer = new char[bufferSize];
        
        file.open(filename, ios::binary);
        if (!file.is_open()) {
            throw runtime_error("Failed to open file: " + filename);
        }
    }

    ~BufferedFileReader() {
        delete[] buffer;
        if (file.is_open()) file.close();
    }

    // Reads a chunk and returns it as a string along with previously split tokens
    bool readChunk(string& chunkData) {
        if (!file && leftover.empty()) return false;

        file.read(buffer, bufferSize);
        streamsize bytesRead = file.gcount();
        
        if (bytesRead == 0) {
            chunkData = leftover;
            leftover.clear();
            return !chunkData.empty();
        }

        string currentChunk(buffer, bytesRead);
        
        // Find the last non-alphanumeric character to split safely
        size_t lastSeparator = string::npos;
        for (long long i = bytesRead - 1; i >= 0; --i) {
            if (!isalnum(currentChunk[i])) {
                lastSeparator = i;
                break;
            }
        }

        if (lastSeparator != string::npos) {
            chunkData = leftover + currentChunk.substr(0, lastSeparator + 1);
            leftover = currentChunk.substr(lastSeparator + 1);
        } else {
            leftover += currentChunk;
            chunkData = ""; 
        }

        return true;
    }
};

class Tokenizer {
public:
    // Extracts words from text, normalizes to lowercase, and handles non-alphanumeric characters as end of words. 
    static vector<string> tokenize(const string& text) {
        vector<string> words;
        string currentWord = "";
        
        for (char c : text) {
            if (isalnum(c)) {
                currentWord += tolower(c); 
            } else if (!currentWord.empty()) {
                words.push_back(currentWord);
                currentWord = "";
            }
        }
        if (!currentWord.empty()) {
            words.push_back(currentWord);
        }
        return words;
    }
};


class VersionedIndex {
private:
    unordered_map<string, int> frequencyMap;
    string versionName;

public:
    VersionedIndex(const string& version) : versionName(version) {}

    // Function Overloading  
    void addWord(const string& word) {
        frequencyMap[word]++;
    }
    
    void addWord(const string& word, int count) {
        frequencyMap[word] += count;
    }

    int getFrequency(const string& word) const {
        auto it = frequencyMap.find(word);
        return it != frequencyMap.end() ? it->second : 0;
    }

    const unordered_map<string, int>& getMap() const {
        return frequencyMap;
    }
    
    string getVersion() const { 
        return versionName; 
    }
};

// Abstract base class
class QueryProcessor {
public:
    virtual void execute() = 0; // virtual function
    virtual ~QueryProcessor() = default;
};

class WordQueryProcessor : public QueryProcessor {
private:
    VersionedIndex& index;
    string targetWord;
public:
    WordQueryProcessor(VersionedIndex& idx, const string& word) : index(idx), targetWord(word) {
        // Ensure query target is case-insensitive
        transform(targetWord.begin(), targetWord.end(), targetWord.begin(), ::tolower);
    }
    
    void execute(){
        cout << "Word Count Result: '" << targetWord << "' -> " 
             << index.getFrequency(targetWord) << "\n";
    }
};

class TopKQueryProcessor : public QueryProcessor {
private:
    VersionedIndex& index;
    int k;
public:
    TopKQueryProcessor(VersionedIndex& idx, int topK) : index(idx), k(topK) {}
    
    void execute(){
        using Pair = pair<int, string>;
        priority_queue<Pair, vector<Pair>, greater<Pair>> minHeap;

        for (const auto& entry : index.getMap()) {
            minHeap.push({entry.second, entry.first});
            if (minHeap.size() > (size_t)k) {
                minHeap.pop();
            }
        }

        cout << "Top-" << k << " words:\n";
        printTopKQueue(minHeap); // Using the required template
    }
};

class DiffQueryProcessor : public QueryProcessor {
private:
    VersionedIndex& index1;
    VersionedIndex& index2;
    string targetWord;
public:
    DiffQueryProcessor(VersionedIndex& idx1, VersionedIndex& idx2, const string& word) 
        : index1(idx1), index2(idx2), targetWord(word) {
        transform(targetWord.begin(), targetWord.end(), targetWord.begin(), ::tolower);
    }

    void execute() {
        int freq1 = index1.getFrequency(targetWord);
        int freq2 = index2.getFrequency(targetWord);
        cout << "Difference Result for '" << targetWord << "':\n";
        cout << index1.getVersion() << ": " << freq1 << " | " << index2.getVersion() << ": " << freq2 << "\n";
        cout << "Difference: " << (freq1 - freq2) << "\n";
    }
};


void buildIndex(const string& filepath, size_t bufferKb, VersionedIndex& index) {
    BufferedFileReader reader(filepath, bufferKb);
    string chunk;
    while (reader.readChunk(chunk)) {
        vector<string> words = Tokenizer::tokenize(chunk);
        for (const string& w : words) {
            index.addWord(w);
        }
    }
}

int main(int argc, char* argv[]) {
    auto start_time = high_resolution_clock::now();

    string file1, file2, version1, version2, queryType, targetWord;
    int bufferKb = -1;
    int topK = 0;


    try {
        for (int i = 1; i < argc; ++i) {
            string arg = argv[i];
            if (i + 1 >= argc || string(argv[i + 1]).substr(0, 2) == "--") {
                throw invalid_argument("Missing or invalid value for argument: " + arg);
            }
            if (arg == "--file") file1 = argv[++i];
            else if (arg == "--file1") file1 = argv[++i];
            else if (arg == "--file2") file2 = argv[++i];
            else if (arg == "--version") version1 = argv[++i];
            else if (arg == "--version1") version1 = argv[++i];
            else if (arg == "--version2") version2 = argv[++i];
            else if (arg == "--buffer") bufferKb = stoi(argv[++i]);
            else if (arg == "--query") queryType = argv[++i];
            else if (arg == "--word") targetWord = argv[++i];
            else if (arg == "--top") topK = stoi(argv[++i]);
            else throw invalid_argument("Unknown argument: " + arg);
        }
         // using extensive error handling to validate and provide clear error for different fringe cases in command lines   
        if (queryType.empty()) {
            throw invalid_argument("You must specify a query type using --query (word, top, or diff).");
        }
        
        if (queryType == "word") {
            if (file1.empty() || version1.empty() || targetWord.empty() || bufferKb==-1) {
                throw invalid_argument("Error: A 'word' query requires --file, --version, --word, and --buffer.");
            }
        } 
        else if (queryType == "top") {
            if (file1.empty() || version1.empty() || bufferKb==-1) {
                throw invalid_argument("Error: A 'top' query requires --file, --version, --buffer,and a valid --top (>= 1).");
            }
        } 
        else if (queryType == "diff") {
            if (file1.empty() || file2.empty() || version1.empty() || version2.empty() || targetWord.empty()|| bufferKb==-1) {
                throw invalid_argument("Error: A 'diff' query requires --file1, --file2, --version1, --version2, --word, and --buffer.");
            }
        } 
        else {
            throw invalid_argument("Error: Invalid query type '" + queryType + "'. Allowed: word, top, diff.");
        }
        
        if (bufferKb < 256 || bufferKb > 1024) {
             throw invalid_argument("Buffer size must be between 256 KB and 1024 KB.");
        }
        
        if (topK < 1 && queryType == "top") {
            throw invalid_argument("Top K must be a positive integer.");
        }
        cout << "Allocated Buffer Size: " << bufferKb << " KB\n";
        if (queryType == "word" || queryType == "top") {
            cout << "Version: " << version1 << "\n"; 
            VersionedIndex index(version1);
            buildIndex(file1, bufferKb, index);

            if (queryType == "word") {
                WordQueryProcessor processor(index, targetWord);
                processor.execute(); 
            } else if (queryType == "top") {
                TopKQueryProcessor processor(index, topK);
                processor.execute(); 
            }

        } else if (queryType == "diff") {
            cout << "Versions: " << version1 << ", " << version2 << "\n"; 
            VersionedIndex idx1(version1);
            VersionedIndex idx2(version2);
            
            buildIndex(file1, bufferKb, idx1);
            buildIndex(file2, bufferKb, idx2);

            DiffQueryProcessor processor(idx1, idx2, targetWord);
            processor.execute();
        } else {
            throw invalid_argument("Invalid query type.");
        }

    } catch (const exception& e) { // catching all errors and exceptions
        cerr << "Error: " << e.what() << "\n";
        return 1;

    }

    auto end_time = high_resolution_clock::now();
    duration<double> exec_time = end_time - start_time;
    cout << "Total Execution Time: " << exec_time.count() << " seconds\n"; 
    return 0;
}