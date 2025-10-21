import requests

import json

def process_cve_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(type(data))
    print(len(data))
    print(data.keys())
    print(data['resultsPerPage'])
    print(data['startIndex'])
    print(data['totalResults'])
    print(data['format'])
    print(data['version'])
    print(data['timestamp']) # 更新的最新时间戳
    print(type(data['vulnerabilities']))
    print(len(data['vulnerabilities'])) # 漏洞个数
    print(type(data['vulnerabilities'][0])) # 每个漏洞类型为dict
    print(data['vulnerabilities'][0].keys()) # 每个漏洞的keys仅仅有一个cve
    print(data['vulnerabilities'][0]['cve'].keys())  # dict_keys(['cve'])里包含了每个漏洞相关的信息
    print(data['vulnerabilities'][0]['cve']['descriptions'], "\n\n") #漏洞描述
    print(data['vulnerabilities'][0]['cve']['published'], "\n\n") #漏洞发布时间
    print(data['vulnerabilities'][100]['cve']['vulnStatus'], "\n\n") #分析
    print(data['vulnerabilities'][100]['cve']['metrics'], "\n\n") #漏洞评分CVSS
    print(type(data['vulnerabilities'][100]['cve']['metrics']), "\n\n") #漏洞评分CVSS
    print(data['vulnerabilities'][100]['cve']['metrics'].keys(), "\n\n") #漏洞评分CVSS
    print(data['vulnerabilities'][100]['cve']['metrics']['cvssMetricV31'][0], "\n\n")
    print(data['vulnerabilities'][100]['cve']['metrics']['cvssMetricV31'][0]['cvssData'], "\n\n")



    knowledge_chunks = []
    for item in data.get('vulnerabilities'):
        cve_id = item['cve']['id'] #获取漏洞ID
        cve_published_time = item['cve']['published'] #获取漏洞发布时间
        # print(cve_id)
        description = ""
        for desc in item['cve']['descriptions']:
            # print(desc)
            if desc['lang'] == 'en': # 使用英文描述
                description = desc['value']

        # 获取漏洞评分 cvss V3.1
        cvss_metric = data['vulnerabilities'][100]['cve']['metrics']['cvssMetricV31'][0]['cvssData']
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

        # 添加漏洞评分

        print(chunk_text)

        knowledge_chunks.append(chunk_text)

        # break # 调试专用，记得删除
    
    return knowledge_chunks

 

if __name__ == '__main__':
    file_path = '/home/xd/llm_deploy/menet_agent/cve/cve_data/nvdcve-2.0-recent.json'

    knowledge_chunks = process_cve_file(file_path=file_path)
    print(len(knowledge_chunks))