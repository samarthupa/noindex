import streamlit as st
import requests
from bs4 import BeautifulSoup

def check_index_status(url):
    try:
        response = requests.get(url)
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

def main():
    st.title('URL Index Checker')
    st.write('Enter URLs below (separated by new lines) to check their index status:')

    urls = st.text_area('URLs', height=200)
    urls = urls.split('\n')

    results = []
    for url in urls:
        if url.strip() != '':
            index_status = check_index_status(url.strip())
            results.append((url.strip(), index_status))

    if results:
        st.write('## Results:')
        st.table(results)

if __name__ == '__main__':
    main()
