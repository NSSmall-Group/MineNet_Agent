import os

# os.environ["CUDA_VISIBLE_DEVICES"] = ""  #让嵌入模型跑在CPU上，后面也可以服务化解耦，跑在另一台主机上

import requests

import json

from langchain_core.documents import Document

from langchain_community.embeddings import ModelScopeEmbeddings

from langchain_community.vectorstores import Chroma

def process_cve_file(file_path):
    """
    预处理CVE漏洞
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # print(type(data))
    # print(len(data))
    # print(data.keys())
    # print(data['resultsPerPage'])
    # print(data['startIndex'])
    # print(data['totalResults'])
    # print(data['format'])
    # print(data['version'])
    # print(data['timestamp']) # 更新的最新时间戳
    # print(type(data['vulnerabilities']))
    # print(len(data['vulnerabilities'])) # 漏洞个数
    # print(type(data['vulnerabilities'][0])) # 每个漏洞类型为dict
    # print(data['vulnerabilities'][0].keys()) # 每个漏洞的keys仅仅有一个cve
    # print(data['vulnerabilities'][0]['cve'].keys())  # dict_keys(['cve'])里包含了每个漏洞相关的信息
    # print(data['vulnerabilities'][0]['cve']['descriptions'], "\n\n") #漏洞描述
    # print(data['vulnerabilities'][0]['cve']['published'], "\n\n") #漏洞发布时间
    # print(data['vulnerabilities'][100]['cve']['vulnStatus'], "\n\n") #分析
    # print(data['vulnerabilities'][100]['cve']['metrics'], "\n\n") #漏洞评分CVSS
    # print(type(data['vulnerabilities'][100]['cve']['metrics']), "\n\n") #漏洞评分CVSS
    # print(data['vulnerabilities'][100]['cve']['metrics'].keys(), "\n\n") #漏洞评分CVSS
    # print(data['vulnerabilities'][100]['cve']['metrics']['cvssMetricV31'][0], "\n\n")
    # print("-----------------")
    # print(data['vulnerabilities'][100]['cve']['metrics']['cvssMetricV31'][0]['cvssData'], "\n\n")
    # standard = list(data['vulnerabilities'][20]['cve']['metrics'].keys())[0]
    # print(list(data['vulnerabilities'][20]['cve']['metrics'].keys())[0], "\n\n")
    # print(data['vulnerabilities'][20]['cve']['metrics'][standard][0]['cvssData'])
    # x = list(data['vulnerabilities'][20]['cve']['metrics'].keys())
    # print(x[0], "\n\n")
    # print("-----------------")


    documents = []  #需要处理成一个Document类型
    # knowledge_chunks = []
    for item in data.get('vulnerabilities'):
        cve_id = item['cve']['id'] #获取漏洞ID
        cve_published_time = item['cve']['published'] #获取漏洞发布时间
        # print(cve_id)
        description = ""
        for desc in item['cve']['descriptions']:
            # print(desc)
            if desc['lang'] == 'en': # 使用英文描述
                description = desc['value']

        # 获取漏洞评分 
        cvss_standard = list(item['cve']['metrics'].keys())  #获取漏洞评分标准
        if len(cvss_standard) == 0:  # 有的漏洞还没有评分标准
            cvss_metric = 'N/A' 
            cvss_version = 'N/A'
            cvss_score = 'N/A'
            cvss_severity = 'N/A'
        else:
            cvss_metric = item['cve']['metrics'][cvss_standard[0]][0]['cvssData']
            cvss_version = cvss_metric['version'] # 评分标准版本
            cvss_score = cvss_metric['baseScore'] # 评分
            cvss_severity = cvss_metric['baseSeverity'] # 严重程度
        
        # print(description)

        # 先只拼接漏洞ID和描述
        chunk_text = (f"漏洞ID：{cve_id}\n" 
                      f"漏洞发布时间：{cve_published_time}\n"
                      f"漏洞描述：{description}\n"
                      f"评分标准版本：CVSS V{cvss_version}\n"
                      f"CVSS评分：{cvss_score}\n"
                      f"CVSS严重程度：{cvss_severity}\n" 
                    )

        # print(chunk_text)

        # knowledge_chunks.append(chunk_text)

        metadata = {
            "cve_id": cve_id,
            "base_score": cvss_score
        }

        doc = Document(page_content=chunk_text, metadata=metadata)
        documents.append(doc)

        # break # 调试专用，记得删除
    
    return documents


def create_vector_database(documents, vec_db_dir):

    local_embedding_model_path = '/home/xd/llm_model/nlp_gte_sentence-embedding_chinese-large'
    
    if not os.path.isdir(local_embedding_model_path):
        print("模型不存在，请检查或者从官方下载")
        exit()
    
    embedding_function = ModelScopeEmbeddings(
        model_id=local_embedding_model_path
    )

    print("----------------------------------Embeddings模型加载完毕-----------------------------------\n\n")

    if not os.path.exists(vec_db_dir):
        print("----------------------------------未发现向量数据库，开始首次构建...\n\n----------------------------------") 

        if documents:
            vector_db = Chroma.from_documents(
                documents=documents,
                embedding=embedding_function,
                persist_directory=vec_db_dir
            )

            print("----------------------------------数据库构建完成----------------------------------")
        else:
            exit("未能成功加载文档")
    else:
        print("----------------------------------向量数据库已经构建，加载中...----------------------------------")
        vector_db = Chroma(
            persist_directory=vec_db_dir,
            embedding_function=embedding_function
        )
        print("----------------------------------向量数据库加载成功----------------------------------")
    
    retriever = vector_db.as_retriever(search_kwargs={"k": 3}) # k=3, 每次检索返回3个最相关的文档

    return retriever

 
if __name__ == '__main__':
    file_path = '/home/xd/llm_deploy/menet_agent/cve/cve_data/nvdcve-2.0-recent.json'

    cve_knowledge_doc = process_cve_file(file_path=file_path)
    print(len(cve_knowledge_doc))

    cve_vec_db_dir = '/home/xd/llm_deploy/menet_agent/cve/cve_data/cve_vec_db'

    create_vector_database(documents=cve_knowledge_doc, vec_db_dir=cve_vec_db_dir)
