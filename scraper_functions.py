import urllib.request
import lxml.html
from lxml import etree
import re

htmlparser = etree.HTMLParser()
random_page = 'https://en.wikipedia.org/wiki/Special:Random'

def read_page(url):
    with urllib.request.urlopen(url) as response:
        if response.code == 200:
            tree = etree.parse(response, htmlparser)

            return tree, response.geturl()
        
        else:
            raise ConnectionError(url)

def get_nth_link(url, n=2):
    tree, page_url = read_page(url)

    # Needed in case title is italic
    title = ''.join(tree.xpath('//*[@id="firstHeading"]')[0].itertext())

    content = tree.xpath('//*[@id="mw-content-text"]/div[1]')[0]

    # Remove elements with a class, like the toc and disambiguation headers
    removals = content.xpath('.//*[@class or @id]')
    
    # But keep the divs with class = 'div-col', 'mw-redirect', or 'wikitable'
    filter_removals = lambda elem: not (elem.get('class') in ('div-col', 'mw-redirect', 'wikitable'))
    removals = filter(filter_removals, removals)
    
    for x in removals:
        x.getparent().remove(x)
        
    # Get all remaining links
    links = [link.get('href') for link in content.findall('.//a')]
    
    # This allows things of the form #... or /wiki/... but disallows #cite_... and /wiki/*:...
    # Because /wiki/*: pages are not article pages (i.e. /wiki/Help: or /wiki/Special:)
    # And #cite_... are citations/notes
    link_check = lambda link: re.match(r'(\/wiki\/(?!([a-zA-Z]+:))|#(?!(cite_)))', str(link))!=None
    valid_links = list(filter(link_check, links))
    
    if len(valid_links)<n:
        return (title, page_url, None)
    
    link_frag = valid_links[n-1]
    
    if link_frag[0] == '#':
        # In case link just links back to page
        second_link = page_url
    else:
        # In case link is /wiki/page#section
        link_frag = re.match(r'^[^#]*', link_frag).group()
        
        second_link = 'https://en.wikipedia.org' + link_frag
    
    return title, page_url, second_link

def make_network(seed_num, n=2):
    visited_pages = dict()
    for i in range(seed_num):
        current_title, _, next_url = get_nth_link(random_page, n=n)

        node = current_title
        #print(f'New Starting Point: {current_title},    {i+1}/{seed_num}')
        for _ in range(100):
            if node in visited_pages:
                #print(f'Joined network on {node}')
                break

            if next_url == None:
                #print(current_url, next_url)
                visited_pages[node] = None
                break

            current_title, _, next_url = get_nth_link(next_url, n=n)

            visited_pages[node] = current_title

            node = current_title
            
    return visited_pages

def add_to_network(visited_pages, seed=None, n=2):
    if seed == None:
        seed = random_page
    new_pages = dict()
    current_title, _, next_url = get_nth_link(seed, n=n)

    node = current_title
    for _ in range(100):
        if node in visited_pages:
            #print('END! on rejoin')
            return new_pages, node

        if node in new_pages:
            break
            
        if next_url == None:
            #print(current_url, next_url)
            new_pages[node] = None
            break

        current_title, _, next_url = get_nth_link(next_url, n=n)

        new_pages[node] = current_title

        node = current_title

    return new_pages, None