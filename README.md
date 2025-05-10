## 1. Agent Design

### 1.1 Overall architecture and structure of agent using ADK framework
The agent has the following files
```
MULTI_TOOL_AGENT/
├── __init__.py
├── agent.py
└── HSN.csv
```

`agent.py` contains the tools the agent requires. Also it is where instantiation of the agent takes place.
### 1.2 Key components of your agent
**Intents**: it represents what the user wants, the goal behind their prompt, after the LLM recognizes the intent, we can use fulfillment logic. ex. Is 010110 valid?
**Entities**: it is the key pieces of information we need to pull out from a user's prompt to fulfill the intent. For example in the promtp "Is 010110 valid?", the enitity is 010110.

**Fulfillment logic**: it is the code that actually does the work and produces a response.
```python
code_str = code_str.strip()

if not (MIN_HSN_CODE_LENGTH <= len(code_str) <= MAX_HSN_CODE_LENGTH):

return {

"status": "error",

"message": (

f"HSN code '{code_str}' must be between "

f"{MIN_HSN_CODE_LENGTH} and {MAX_HSN_CODE_LENGTH} digits."

)

}

if not code_str.isdigit():

return {

"status": "error",

"message": f"HSN code '{code_str}' contains non-numeric characters."

}

if code_str in _hsn_map:

return {

"status": "success",

"message": f"HSN code {code_str} is valid.",

"description": _hsn_map[code_str]

}

else:

return {

"status": "error",

"message": f"HSN code {code_str} not found."

}
```

### 1.3 Agent handling user input (eg. a single HSN code, multiple HSN codes)
The agent can handle multiple user inputs if separated by commas. Other separation methods can also be used. 

| Agent                                | User                                 |
| ------------------------------------ | ------------------------------------ |
|                                      | ![[Pasted image 20250510115453.png]] |
| ![[Pasted image 20250510115510.png]] |                                      |
![[Pasted image 20250510120017.png]]

### 1.4 Agent providing its validation output
Based on check the agent will parse the returned json and show the output.

---
## 2. Data Handling

### 2.1 Agent's access to file and processing of data
1. The file is loaded and read into memory once using `pandas`.
2. The columns and column keys are normalized by removing whitespace. Other normalization like missing values etc. should be done before feeding the agent the file.
3. Build in-memory index
	- A dict mapping code→description for O(1) lookups.
4. When the agent calls tool `validate_HSNcode` only the code runs the file is not loaded again
### 2.2 Pre-processed vs Loaded on demand

| Property     | Load at startup (Pre-processing)                | On-demand loading                                  |
| ------------ | ----------------------------------------------- | -------------------------------------------------- |
| Latency      | One time startup cost                           | Every quesry will incur parsing and I/O operations |
| Memory usage | Entire dataset and index in memory              | -                                                  |
| Complexity   | Simple                                          | Require chunking can become complex                |
| Scalability  | Can handle many codes if server has enough ram. | -                                                  |
IMO, Since this is HSN lookup agent where the file is reltively static pre-processing is ideal if there are hundreds to thousands of queries and server has enough ram. There will be a slow startup in exchange for fast per query response.

---
## 3. Validation Logic

### 3.1 Format Validation
The format of the user provided string is checked, the lenght is compared with minimum and max lenght, also it is checked if the code provided are digits. See [Fulfillment logic](#12-key-components-of-your-agent).
### 3.2 Existence Validation
Existence validation check takes O(1) time complexity since it just an key check in python's `dict`.

### 3.3 Hierarchical validation
For standard HSN codes there is 2-digit, 4-digit, and 6-digit and full code 8-digit.
for 8 digit code like 01011010, its parents can found by:
```python
code = "01011010"
parents = [ code[:L] for L in LEVEL_LENGTHS ]  
# which gives us ["01", "0101", "010110"]
```

We can then check each parent in map:
```python
missing = [p for p in parents if p not in _hsn_map]
```

missing will be a boolean value. if true we can tell that parent levels are missing, if false we can tell all parent levels are valid.

---
## 4. Agent Response

### 4.1 Valid HSN code

Note: When there are multiple HSN codes provided by the user, the agent will list them out in a tabular form. 

| Agent                                | User                                 |
| ------------------------------------ | ------------------------------------ |
|                                      | ![[Pasted image 20250510104804.png]] |
| ![[Pasted image 20250510104824.png]] |                                      |
|                                      | ![[Pasted image 20250510104551.png]] |
| ![[Pasted image 20250510105023.png]] |                                      |

### 4.2 Invalid HSN code

| Agent                                | User                                 |
| ------------------------------------ | ------------------------------------ |
|                                      | ![[Pasted image 20250510105236.png]] |
| ![[Pasted image 20250510105254.png]] |                                      |
|                                      | ![[Pasted image 20250510105147.png]] |
| ![[Pasted image 20250510105203.png]] |                                      |

