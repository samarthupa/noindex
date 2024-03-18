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
    with st.spinner('Processing...'):
        total_urls = len(urls)
        progress_bar = st.progress(0)
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            future_to_url = {executor.submit(check_index_status, url): url for url in urls}
            for i, future in enumerate(concurrent.futures.as_completed(future_to_url)):
                url = future_to_url[future]
                try:
                    result = future.result()
                    results.append((url, result))
                except Exception as e:
                    results.append((url, str(e)))
                progress = (i + 1) / total_urls
                progress_bar.progress(progress)
    return results

def main():
    st.title('URL Index Checker')
    st.write('Enter URLs below (separated by new lines) to check their index status:')

    urls = st.text_area('URLs', height=200)
    urls = urls.split('\n')

    if st.button('Check URLs'):
        results = check_urls(urls)
        st.write('## Results:')
        st.table(results)

        # Download CSV button
        if len(results) > 0:
            df = pd.DataFrame(results, columns=['URL', 'Index Status'])
            csv = df.to_csv(index=False)
            b64 = base64.b64encode(csv.encode()).decode()
            href = f'<a href="data:file/csv;base64,{b64}" download="url_index_results.csv">Download CSV</a>'
            st.markdown(href, unsafe_allow_html=True)

if __name__ == '__main__':
    main()
