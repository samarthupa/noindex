import streamlit as st
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import concurrent.futures
import pandas as pd
import base64

def check_index_status(url):
    try:
        ua = UserAgent()
        headers = {'User-Agent': ua.chrome}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        meta_tags = soup.find_all('meta')
        index_status = 'Unknown'

        for tag in meta_tags:
            if 'name' in tag.attrs and tag.attrs['name'].lower() == 'robots':
                content = tag.attrs['content'].lower()
                if 'noindex' in content:
                    index_status = 'Noindex'
                elif 'index' in content:
                    index_status = 'Index'

        if index_status == 'Unknown':
            return 'No meta robots tag found'
        else:
            return index_status
    except Exception as e:
        return str(e)

def check_urls(urls):
    results = []
    processed_count = 0
    total_urls = len(urls)
    with st.spinner('Processing...'):
        for result in concurrent.futures.ThreadPoolExecutor(max_workers=10).map(check_index_status, urls):
            results.append(result)
            processed_count += 1
            st.text(f"Processed {processed_count}/{total_urls} URLs", False)
    return results

def main():
    st.title('URL Index Checker')
    st.write('Enter URLs below (separated by new lines) to check their index status:')

    urls = st.text_area('URLs', height=200)
    urls = urls.split('\n')

    if st.button('Check URLs'):
        results = check_urls(urls)
        st.write('## Results:')
        df = pd.DataFrame(list(zip(urls, results)), columns=['URL', 'Index Status'])
        st.table(df)
        st.markdown(get_table_download_link(df), unsafe_allow_html=True)

def get_table_download_link(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="index_results.csv">Download CSV File</a>'
    return href

if __name__ == '__main__':
    main()
