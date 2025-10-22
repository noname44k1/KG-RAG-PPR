"""
Reference:
 - Prompts are from [graphrag](https://github.com/microsoft/graphrag)
"""

GRAPH_FIELD_SEP = "<SEP>"
PROMPTS = {}

PROMPTS[
    "claim_extraction"
] = """-Target activity-
You are an intelligent assistant that helps a human analyst to analyze claims against certain entities presented in a text document.

-Goal-
Given a text document that is potentially relevant to this activity, an entity specification, and a claim description, extract all entities that match the entity specification and all claims against those entities.

-Steps-
1. Extract all named entities that match the predefined entity specification. Entity specification can either be a list of entity names or a list of entity types.
2. For each entity identified in step 1, extract all claims associated with the entity. Claims need to match the specified claim description, and the entity should be the subject of the claim.
For each claim, extract the following information:
- Subject: name of the entity that is subject of the claim, capitalized. The subject entity is one that committed the action described in the claim. Subject needs to be one of the named entities identified in step 1.
- Object: name of the entity that is object of the claim, capitalized. The object entity is one that either reports/handles or is affected by the action described in the claim. If object entity is unknown, use **NONE**.
- Claim Type: overall category of the claim, capitalized. Name it in a way that can be repeated across multiple text inputs, so that similar claims share the same claim type
- Claim Status: **TRUE**, **FALSE**, or **SUSPECTED**. TRUE means the claim is confirmed, FALSE means the claim is found to be False, SUSPECTED means the claim is not verified.
- Claim Description: Detailed description explaining the reasoning behind the claim, together with all the related evidence and references.
- Claim Date: Period (start_date, end_date) when the claim was made. Both start_date and end_date should be in ISO-8601 format. If the claim was made on a single date rather than a date range, set the same date for both start_date and end_date. If date is unknown, return **NONE**.
- Claim Source Text: List of **all** quotes from the original text that are relevant to the claim.

Format each claim as (<subject_entity>{tuple_delimiter}<object_entity>{tuple_delimiter}<claim_type>{tuple_delimiter}<claim_status>{tuple_delimiter}<claim_start_date>{tuple_delimiter}<claim_end_date>{tuple_delimiter}<claim_description>{tuple_delimiter}<claim_source>)

3. Return output in English as a single list of all the claims identified in steps 1 and 2. Use **{record_delimiter}** as the list delimiter.

4. When finished, output {completion_delimiter}

-Examples-
Example 1:
Entity specification: organization
Claim description: red flags associated with an entity
Text: According to an article on 2022/01/10, Company A was fined for bid rigging while participating in multiple public tenders published by Government Agency B. The company is owned by Person C who was suspected of engaging in corruption activities in 2015.
Output:

(COMPANY A{tuple_delimiter}GOVERNMENT AGENCY B{tuple_delimiter}ANTI-COMPETITIVE PRACTICES{tuple_delimiter}TRUE{tuple_delimiter}2022-01-10T00:00:00{tuple_delimiter}2022-01-10T00:00:00{tuple_delimiter}Company A was found to engage in anti-competitive practices because it was fined for bid rigging in multiple public tenders published by Government Agency B according to an article published on 2022/01/10{tuple_delimiter}According to an article published on 2022/01/10, Company A was fined for bid rigging while participating in multiple public tenders published by Government Agency B.)
{completion_delimiter}

Example 2:
Entity specification: Company A, Person C
Claim description: red flags associated with an entity
Text: According to an article on 2022/01/10, Company A was fined for bid rigging while participating in multiple public tenders published by Government Agency B. The company is owned by Person C who was suspected of engaging in corruption activities in 2015.
Output:

(COMPANY A{tuple_delimiter}GOVERNMENT AGENCY B{tuple_delimiter}ANTI-COMPETITIVE PRACTICES{tuple_delimiter}TRUE{tuple_delimiter}2022-01-10T00:00:00{tuple_delimiter}2022-01-10T00:00:00{tuple_delimiter}Company A was found to engage in anti-competitive practices because it was fined for bid rigging in multiple public tenders published by Government Agency B according to an article published on 2022/01/10{tuple_delimiter}According to an article published on 2022/01/10, Company A was fined for bid rigging while participating in multiple public tenders published by Government Agency B.)
{record_delimiter}
(PERSON C{tuple_delimiter}NONE{tuple_delimiter}CORRUPTION{tuple_delimiter}SUSPECTED{tuple_delimiter}2015-01-01T00:00:00{tuple_delimiter}2015-12-30T00:00:00{tuple_delimiter}Person C was suspected of engaging in corruption activities in 2015{tuple_delimiter}The company is owned by Person C who was suspected of engaging in corruption activities in 2015)
{completion_delimiter}

-Real Data-
Use the following input for your answer.
Entity specification: {entity_specs}
Claim description: {claim_description}
Text: {input_text}
Output: """

PROMPTS[
    "community_report"
] = """You are an AI assistant that helps a human analyst to perform general information discovery. 
Information discovery is the process of identifying and assessing relevant information associated with certain entities (e.g., organizations and individuals) within a network.

# Goal
Write a comprehensive report of a community, given a list of entities that belong to the community as well as their relationships and optional associated claims. The report will be used to inform decision-makers about information associated with the community and their potential impact. The content of this report includes an overview of the community's key entities, their legal compliance, technical capabilities, reputation, and noteworthy claims.

# Report Structure

The report should include the following sections:

- TITLE: community's name that represents its key entities - title should be short but specific. When possible, include representative named entities in the title.
- SUMMARY: An executive summary of the community's overall structure, how its entities are related to each other, and significant information associated with its entities.
- IMPACT SEVERITY RATING: a float score between 0-10 that represents the severity of IMPACT posed by entities within the community.  IMPACT is the scored importance of a community.
- RATING EXPLANATION: Give a single sentence explanation of the IMPACT severity rating.
- DETAILED FINDINGS: A list of 5-10 key insights about the community. Each insight should have a short summary followed by multiple paragraphs of explanatory text grounded according to the grounding rules below. Be comprehensive.

Return output as a well-formed JSON-formatted string with the following format:
    {{
        "title": <report_title>,
        "summary": <executive_summary>,
        "rating": <impact_severity_rating>,
        "rating_explanation": <rating_explanation>,
        "findings": [
            {{
                "summary":<insight_1_summary>,
                "explanation": <insight_1_explanation>
            }},
            {{
                "summary":<insight_2_summary>,
                "explanation": <insight_2_explanation>
            }}
            ...
        ]
    }}

# Grounding Rules
Do not include information where the supporting evidence for it is not provided.


# Example Input
-----------
Text:
```
Entities:
```csv
id,entity,type,description
5,VERDANT OASIS PLAZA,geo,Verdant Oasis Plaza is the location of the Unity March
6,HARMONY ASSEMBLY,organization,Harmony Assembly is an organization that is holding a march at Verdant Oasis Plaza
```
Relationships:
```csv
id,source,target,description
37,VERDANT OASIS PLAZA,UNITY MARCH,Verdant Oasis Plaza is the location of the Unity March
38,VERDANT OASIS PLAZA,HARMONY ASSEMBLY,Harmony Assembly is holding a march at Verdant Oasis Plaza
39,VERDANT OASIS PLAZA,UNITY MARCH,The Unity March is taking place at Verdant Oasis Plaza
40,VERDANT OASIS PLAZA,TRIBUNE SPOTLIGHT,Tribune Spotlight is reporting on the Unity march taking place at Verdant Oasis Plaza
41,VERDANT OASIS PLAZA,BAILEY ASADI,Bailey Asadi is speaking at Verdant Oasis Plaza about the march
43,HARMONY ASSEMBLY,UNITY MARCH,Harmony Assembly is organizing the Unity March
```
```
Output:
{{
    "title": "Verdant Oasis Plaza and Unity March",
    "summary": "The community revolves around the Verdant Oasis Plaza, which is the location of the Unity March. The plaza has relationships with the Harmony Assembly, Unity March, and Tribune Spotlight, all of which are associated with the march event.",
    "rating": 5.0,
    "rating_explanation": "The impact severity rating is moderate due to the potential for unrest or conflict during the Unity March.",
    "findings": [
        {{
            "summary": "Verdant Oasis Plaza as the central location",
            "explanation": "Verdant Oasis Plaza is the central entity in this community, serving as the location for the Unity March. This plaza is the common link between all other entities, suggesting its significance in the community. The plaza's association with the march could potentially lead to issues such as public disorder or conflict, depending on the nature of the march and the reactions it provokes."
        }},
        {{
            "summary": "Harmony Assembly's role in the community",
            "explanation": "Harmony Assembly is another key entity in this community, being the organizer of the march at Verdant Oasis Plaza. The nature of Harmony Assembly and its march could be a potential source of threat, depending on their objectives and the reactions they provoke. The relationship between Harmony Assembly and the plaza is crucial in understanding the dynamics of this community."
        }},
        {{
            "summary": "Unity March as a significant event",
            "explanation": "The Unity March is a significant event taking place at Verdant Oasis Plaza. This event is a key factor in the community's dynamics and could be a potential source of threat, depending on the nature of the march and the reactions it provokes. The relationship between the march and the plaza is crucial in understanding the dynamics of this community."
        }},
        {{
            "summary": "Role of Tribune Spotlight",
            "explanation": "Tribune Spotlight is reporting on the Unity March taking place in Verdant Oasis Plaza. This suggests that the event has attracted media attention, which could amplify its impact on the community. The role of Tribune Spotlight could be significant in shaping public perception of the event and the entities involved."
        }}
    ]
}}


# Real Data

Use the following text for your answer. Do not make anything up in your answer.

Text:
```
{input_text}
```

The report should include the following sections:

- TITLE: community's name that represents its key entities - title should be short but specific. When possible, include representative named entities in the title.
- SUMMARY: An executive summary of the community's overall structure, how its entities are related to each other, and significant information associated with its entities.
- IMPACT SEVERITY RATING: a float score between 0-10 that represents the severity of IMPACT posed by entities within the community.  IMPACT is the scored importance of a community.
- RATING EXPLANATION: Give a single sentence explanation of the IMPACT severity rating.
- DETAILED FINDINGS: A list of 5-10 key insights about the community. Each insight should have a short summary followed by multiple paragraphs of explanatory text grounded according to the grounding rules below. Be comprehensive.

Return output as a well-formed JSON-formatted string with the following format:
    {{
        "title": <report_title>,
        "summary": <executive_summary>,
        "rating": <impact_severity_rating>,
        "rating_explanation": <rating_explanation>,
        "findings": [
            {{
                "summary":<insight_1_summary>,
                "explanation": <insight_1_explanation>
            }},
            {{
                "summary":<insight_2_summary>,
                "explanation": <insight_2_explanation>
            }}
            ...
        ]
    }}

# Grounding Rules
Do not include information where the supporting evidence for it is not provided.

Output:
"""

PROMPTS[
    "entity_extraction"
] = """-Mục tiêu-
Cho một tài liệu văn bản về hỏi đáp y tế và một danh sách các loại thực thể, hãy xác định tất cả các thực thể thuộc các loại đó từ văn bản và tất cả các mối quan hệ giữa các thực thể đã xác định.

-Các bước-
1. Xác định tất cả các thực thể. Với mỗi thực thể được xác định, trích xuất các thông tin sau:
entity_name: Tên của thực thể, viết hoa
entity_type: Một trong các loại sau: [{entity_types}]
entity_description: Mô tả ngắn gọn về các thuộc tính của thực thể
Định dạng mỗi thực thể như sau: ("entity"{tuple_delimiter}<entity_name>{tuple_delimiter}<entity_type>{tuple_delimiter}<entity_description>)


2. Từ các thực thể đã xác định ở bước 1, xác định tất cả các cặp (source_entity, target_entity) rõ ràng có liên quan với nhau.
Với mỗi cặp thực thể có liên quan, trích xuất các thông tin sau:
- source_entity: tên của source entity, như đã xác định ở bước 1
- target_entity: tên của target entity, như đã xác định ở bước 1
- relationship_description: giải thích tại sao bạn nghĩ hai thực thể source entity và the target entity có liên quan với nhau
- relationship_strength: điểm số thể hiện mức độ mạnh của mối quan hệ giữa source entity và the target entity
Định dạng mỗi mối quan hệ như sau: ("relationship"{tuple_delimiter}<source_entity>{tuple_delimiter}<target_entity>{tuple_delimiter}<relationship_description>{tuple_delimiter}<relationship_strength>)

3. Trả về kết quả dưới dạng 1 danh sách duy nhất gồm tất cả các thực thể và mối quan hệ đã xác định trong bước 1 và 2. Sử dụng **{record_delimiter}** làm dấu phân cách danh sách.

4. Khi hoàn tất, xuất ra {completion_delimiter}

######################
-Ví dụ-
Entity_types: [người, bộ phận cơ thể, bệnh, tổ chức, địa điểm, phương pháp điều trị, thuốc, lời khuyên]

Văn bản:
Hẹp van tim xảy ra khi van trong trái tim không hoạt động đúng cách, gây ra sự hạn chế lưu thông máu. Điều này có thể gây ra nhiều vấn đề khó khăn cho tim và có thể dẫn đến những biến chứng nguy hiểm như suy tim, đau thắt ngực, suy hô hấp, hay thậm chí gây tử vong nếu không được điều trị kịp thời.
################
Output:
("entity"{tuple_delimiter}HẸP VAN TIM{tuple_delimiter}bệnh{tuple_delimiter}Van tim bị hẹp, cản trở lưu thông máu){record_delimiter}
("entity"{tuple_delimiter}TIM{tuple_delimiter}bộ phận cơ thể{tuple_delimiter}Cơ quan bơm máu trong cơ thể){record_delimiter}
("entity"{tuple_delimiter}SUY TIM{tuple_delimiter}bệnh{tuple_delimiter}Tim không bơm máu hiệu quả){record_delimiter}
("entity"{tuple_delimiter}ĐAU THẮT NGỰC{tuple_delimiter}bệnh{tuple_delimiter}Đau ngực do thiếu máu đến tim){record_delimiter}
("entity"{tuple_delimiter}SUY HÔ HẤP{tuple_delimiter}bệnh{tuple_delimiter}Thiếu oxy do tim phổi hoạt động kém){record_delimiter}
("entity"{tuple_delimiter}ĐIỀU TRỊ KỊP THỜI{tuple_delimiter}lời khuyên{tuple_delimiter}Nên điều trị sớm để tránh biến chứng){record_delimiter}
("relationship"{tuple_delimiter}HẸP VAN TIM{tuple_delimiter}TIM{tuple_delimiter}Hẹp van tim làm giảm khả năng lưu thông máu qua tim{tuple_delimiter}6){record_delimiter}
("relationship"{tuple_delimiter}HẸP VAN TIM{tuple_delimiter}SUY TIM{tuple_delimiter}Hẹp van tim gây quá tải cho tim dẫn đến suy tim{tuple_delimiter}7){record_delimiter}
("relationship"{tuple_delimiter}HẸP VAN TIM{tuple_delimiter}ĐAU THẮT NGỰC{tuple_delimiter}Thiếu máu đến tim do van hẹp có thể gây đau thắt ngực{tuple_delimiter}6){record_delimiter}
("relationship"{tuple_delimiter}HẸP VAN TIM{tuple_delimiter}SUY HÔ HẤP{tuple_delimiter}Giảm lưu lượng máu gây thiếu oxy dẫn đến suy hô hấp{tuple_delimiter}5){record_delimiter}
("relationship"{tuple_delimiter}ĐIỀU TRỊ KỊP THỜI{tuple_delimiter}HẸP VAN TIM{tuple_delimiter}Điều trị sớm giúp phòng tránh biến chứng nguy hiểm của hẹp van tim{tuple_delimiter}7){completion_delimiter}
#############################
-Real Data-
######################
Entity_types: {entity_types}
Text: {input_text}
######################
Output:
"""


PROMPTS[
    "summarize_entity_descriptions"
] = """Bạn là một trợ lý hữu ích có trách nhiệm tạo ra một bản tóm tắt toàn diện về dữ liệu được cung cấp bên dưới.
Cho 1 hoặc 2 thực thể và danh sách các mô tả, tất cả đều liên quan đến cùng một thực thể hoặc nhóm thực thể.
Hãy tóm tắt tất cả các mô tả thành một mô tả duy nhất, toàn diện và chính xác về thực thể hoặc nhóm thực thể đó.
Nếu những mô tả được cung cấp là mâu thuẫn, hãy giải quyết các mâu thuẫn và cung cấp một bản tóm tắt duy nhất, mạch lạc.
Hãy đảm bảo bản tóm tắt được viết bằng ngôi thứ ba và bao gồm tên thực thể để chúng tôi có được bối cảnh đầy đủ.

#######
-Dữ liệu-
Thực thể: {entity_name}
Danh sách mô tả: {description_list}
#######
Kết quả:
"""


PROMPTS[
    "entiti_continue_extraction"
] = """Rất nhiều thực thể đã bị bỏ sót trong lần trích xuất trước đó. Hãy thêm chúng vào bên dưới theo định dạng tương tự:
"""

PROMPTS[
    "entiti_if_loop_extraction"
] = """Có vẻ như một số thực thể vẫn còn bị bỏ sót. Hãy trả lời YES | NO nếu vẫn còn thực thể cần được thêm vào.
"""

PROMPTS["DEFAULT_ENTITY_TYPES"] = ["người", "bộ phận cơ thể", "bệnh", "tổ chức", "địa điểm", "phương pháp điều trị", "thuốc", "lời khuyên"]
PROMPTS["DEFAULT_TUPLE_DELIMITER"] = "<|>"
PROMPTS["DEFAULT_RECORD_DELIMITER"] = "##"
PROMPTS["DEFAULT_COMPLETION_DELIMITER"] = "<|COMPLETE|>"

PROMPTS[
    "my_query_system"
] ="Bạn là một chuyên gia trong lĩnh vực y tế và có thể cung cấp thông tin chi tiết về các bệnh lý, phương pháp điều trị và các khuyến nghị liên quan đến sức khỏe."
PROMPTS[
    "my_query"
] = """
---Mục tiêu---
Hãy phân thông tin văn bản và suy luận từ các đường dẫn (paths) trong bảng dữ liệu đầu vào, và kết hợp bất kỳ kiến thức chung nào có liên quan.
Đưa ra câu trả lời đầy đủ, dễ hiểu, thuyết phục cho câu hỏi của người dùng.
Nếu bạn không biết câu trả lời, hãy nói như vậy. Không tạo ra bất cứ điều gì.
Hãy kết thúc bằng cách khuyên nghị người dùng nên tham khảo ý kiến bác sĩ hoặc chuyên gia y tế để có thông tin chính xác và phù hợp nhất với tình trạng sức khỏe của họ.
Định dạng câu trả lời bằng markdown.
---Dữ liệu---

{context_data}

---Câu hỏi---
{question}
"""

PROMPTS[
    "global_map_rag_points"
] = """---Role---

You are a helpful assistant responding to questions about data in the tables provided.


---Goal---

Generate a response consisting of a list of key points that responds to the user's question, summarizing all relevant information in the input data tables.

You should use the data provided in the data tables below as the primary context for generating the response.
If you don't know the answer or if the input data tables do not contain sufficient information to provide an answer, just say so. Do not make anything up.

Each key point in the response should have the following element:
- Description: A comprehensive description of the point.
- Importance Score: An integer score between 0-100 that indicates how important the point is in answering the user's question. An 'I don't know' type of response should have a score of 0.

The response should be JSON formatted as follows:
{{
    "points": [
        {{"description": "Description of point 1...", "score": score_value}},
        {{"description": "Description of point 2...", "score": score_value}}
    ]
}}

The response shall preserve the original meaning and use of modal verbs such as "shall", "may" or "will".
Do not include information where the supporting evidence for it is not provided.


---Data tables---

{context_data}

---Goal---

Generate a response consisting of a list of key points that responds to the user's question, summarizing all relevant information in the input data tables.

You should use the data provided in the data tables below as the primary context for generating the response.
If you don't know the answer or if the input data tables do not contain sufficient information to provide an answer, just say so. Do not make anything up.

Each key point in the response should have the following element:
- Description: A comprehensive description of the point.
- Importance Score: An integer score between 0-100 that indicates how important the point is in answering the user's question. An 'I don't know' type of response should have a score of 0.

The response shall preserve the original meaning and use of modal verbs such as "shall", "may" or "will".
Do not include information where the supporting evidence for it is not provided.

The response should be JSON formatted as follows:
{{
    "points": [
        {{"description": "Description of point 1", "score": score_value}},
        {{"description": "Description of point 2", "score": score_value}}
    ]
}}
"""

PROMPTS[
    "global_reduce_rag_response"
] = """---Role---

You are a helpful assistant responding to questions about a dataset by synthesizing perspectives from multiple analysts.


---Goal---

Generate a response of the target length and format that responds to the user's question, summarize all the reports from multiple analysts who focused on different parts of the dataset.

Note that the analysts' reports provided below are ranked in the **descending order of importance**.

If you don't know the answer or if the provided reports do not contain sufficient information to provide an answer, just say so. Do not make anything up.

The final response should remove all irrelevant information from the analysts' reports and merge the cleaned information into a comprehensive answer that provides explanations of all the key points and implications appropriate for the response length and format.

Add sections and commentary to the response as appropriate for the length and format. Style the response in markdown.

The response shall preserve the original meaning and use of modal verbs such as "shall", "may" or "will".

Do not include information where the supporting evidence for it is not provided.


---Target response length and format---

{response_type}


---Analyst Reports---

{report_data}


---Goal---

Generate a response of the target length and format that responds to the user's question, summarize all the reports from multiple analysts who focused on different parts of the dataset.

Note that the analysts' reports provided below are ranked in the **descending order of importance**.

If you don't know the answer or if the provided reports do not contain sufficient information to provide an answer, just say so. Do not make anything up.

The final response should remove all irrelevant information from the analysts' reports and merge the cleaned information into a comprehensive answer that provides explanations of all the key points and implications appropriate for the response length and format.

The response shall preserve the original meaning and use of modal verbs such as "shall", "may" or "will".

Do not include information where the supporting evidence for it is not provided.


---Target response length and format---

{response_type}

Add sections and commentary to the response as appropriate for the length and format. Style the response in markdown.
"""

PROMPTS[
    "naive_rag_response"
] = """Bạn là chuyên gia trong lĩnh vực y tế.
Dưới đây là những kiến thức mà bạn biết:
{content_data}
---
Nếu bạn không biết câu trả lời hoặc nếu các kiến thức được cung cấp không chứa đủ thông tin để đưa ra câu trả lời, chỉ cần nói như vậy. Không được bịa ra bất kỳ điều gì.
Hãy tạo một câu trả lời có độ dài và định dạng như mục tiêu, phản hồi lại câu hỏi của người dùng bằng cách tóm tắt tất cả thông tin trong bảng dữ liệu đầu vào một cách phù hợp với độ dài và định dạng câu trả lời, đồng thời lồng ghép bất kỳ kiến thức tổng quát nào có liên quan.
Nếu bạn không biết câu trả lời, chỉ cần nói như vậy. Không được bịa ra bất kỳ điều gì.
Không đưa vào thông tin nếu không có bằng chứng hỗ trợ từ dữ liệu.

---Độ dài và định dạng câu trả lời mục tiêu---
{response_type}
"""

PROMPTS["fail_response"] = "Sorry, I'm not able to provide an answer to that question."

PROMPTS["process_tickers"] = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

PROMPTS["default_text_separator"] = [
    # Paragraph separators
    "\n",
    "\n\n",
    "\n\n\n",
    "\n\n\n\n\n",
    "\n\n\n\n\n\n",
]

PROMPTS[
    "local_rag_response"
] = """---Vai trò---

Bạn là chuyên gia trong lĩnh vực y tế, trả lời các câu hỏi liên quan đến dữ liệu trong các bảng đã cung cấp.


---Mục tiêu---

Tạo một câu trả lời với độ dài và định dạng mục tiêu, phản hồi câu hỏi của người dùng bằng cách tóm tắt tất cả thông tin trong các bảng dữ liệu đầu vào một cách phù hợp với độ dài và định dạng câu trả lời, đồng thời lồng ghép bất kỳ kiến thức tổng quát nào có liên quan.
Nếu bạn không biết câu trả lời, chỉ cần nói như vậy. Không được bịa ra bất kỳ điều gì.
Không đưa vào thông tin nếu không có bằng chứng hỗ trợ từ dữ liệu.

---Độ dài và định dạng câu trả lời mục tiêu---

{response_type}


---Bảng dữ liệu---

{context_data}


---Mục tiêu---

Tạo một câu trả lời với độ dài và định dạng mục tiêu, phản hồi câu hỏi của người dùng bằng cách tóm tắt tất cả thông tin trong các bảng dữ liệu đầu vào một cách phù hợp với độ dài và định dạng câu trả lời, đồng thời lồng ghép bất kỳ kiến thức tổng quát nào có liên quan.

Nếu bạn không biết câu trả lời, chỉ cần nói như vậy. Không được bịa ra bất kỳ điều gì.

Không đưa vào thông tin nếu không có bằng chứng hỗ trợ từ dữ liệu.

---Độ dài và định dạng câu trả lời mục tiêu---

{response_type}

Thêm các phần và bình luận vào câu trả lời nếu phù hợp với độ dài và định dạng. Định dạng câu trả lời theo kiểu markdown.
"""

# eval prompts
PROMPTS["my_query_health_care_eval"] = """Bạn là chuyên gia trong lĩnh vực y tế. Hãy trả lời các câu hỏi bên dưới dựa trên thông tin được cung cấp. 
Chỉ tạo câu trả lời dựa trên thông tin trong văn bản được cung cấp.

Dưới đây là thông tin:
{context}

Câu hỏi: {question}
"""