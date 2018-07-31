# -*- coding: utf-8 -*-
#test，more test
import requests
import json
import codecs
import datetime
import sys
default_stdout=sys.stdout
default_stderr=sys.stderr
reload(sys)
sys.stdout=default_stdout
sys.stderr=default_stderr
sys.setdefaultencoding('utf8')


"2014-10-21T20:46:20Z"
TIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


def send_request(data):
    graphql_query = """{{"query":  "{0}"}}""".format(data.replace("\n", " "))
    #print graphql_query
    r = requests.post("https://api.github.com/graphql", graphql_query,
                      headers={'Authorization': 'bearer 96839bc1b872391ee9a3fc49c92c5fa2a6d90281'})
    #print r.text
    return json.loads(r.text)


def parse_commit_history(input):
    has_next = input.get('data').get('repository').get('ref').get('target').get('history').get('pageInfo').get('hasNextPage')
    next_cursor = None
    if has_next:
        next_cursor = input.get('data').get('repository').get('ref').get('target').get('history').get('pageInfo').get('endCursor')
    nodes = input.get('data').get('repository').get('ref').get('target').get('history').get('nodes')

    return has_next, next_cursor, nodes


def fetch_commit_history(owner, name, max_num=None):
    query_template = """ query {{
  repository(owner:\\\"{0}\\\", name:\\\"{1}\\\") {{
    ref(qualifiedName: \\\"refs/heads/master\\\") {{
      target {{
        ... on Commit {{
          history(first:100{2}) {{
            pageInfo {{
              hasNextPage
              endCursor
            }}
            nodes {{
              url
              committedDate
            }}
          }}
        }}
      }}
    }}
  }}
}} """
    commit_history = []
    init_query = query_template.format(owner, name, "")
    init_data = send_request(init_query)
    (has_next, next_cursor, nodes) = parse_commit_history(init_data)
    commit_history.extend(nodes)
    while has_next:
        query = query_template.format(owner, name, """,after:\\\"{0}\\\"""".format(next_cursor))
        data = send_request(query)
        (has_next, next_cursor, nodes) = parse_commit_history(data)
        commit_history.extend(nodes)
        if max_num and len(commit_history) > max_num:
            commit_history = commit_history[:max_num]
            break

    return commit_history


def parse_start_history(input):
    has_next = input.get('data').get('repository').get('stargazers').get('pageInfo').get('hasPreviousPage')
    next_cursor = None
    if has_next:
        next_cursor = input.get('data').get('repository').get('stargazers').get('pageInfo').get('startCursor')
    edges = input.get('data').get('repository').get('stargazers').get('edges')

    return has_next, next_cursor, edges


def fetch_start_history(owner, name, max_num=None):
    """

    :param owner: git project owner
    :param name: git project name
    :param max_num: for debug purpose
    :return: start_history
    """
    query_template = """ query {{
  repository(owner:\\\"{0}\\\", name:\\\"{1}\\\") {{
    stargazers(last:100{2}) {{
      pageInfo {{
        hasPreviousPage
        startCursor
      }}
      edges {{
        node {{
          name
        }}
        starredAt
      }}
    }}
  }}
}} """
    star_history = []
    init_query = query_template.format(owner, name, "")
    init_data = send_request(init_query)
    (has_next, next_cursor, edges) = parse_start_history(init_data)
    star_history.extend(edges[::-1])
    while has_next:
        query = query_template.format(owner, name, """,before:\\\"{0}\\\"""".format(next_cursor))
        data = send_request(query)
        (has_next, next_cursor, edges) = parse_start_history(data)
        star_history.extend(edges[::-1])
        if max_num and len(star_history) > max_num:
            star_history = star_history[:max_num]
            break

    return star_history


def simple_stat(input, key, func):
    count = 0
    for i in input:
        ds = datetime.datetime.strptime(i.get(key), TIME_FORMAT)
        if func(ds):
            count += 1
    return count


if __name__ == "__main__":
    owner = "staryxj"     #按需求换成实际的项目
    name = "hello-world"      #按需求换成实际的项目
    # owner = "MariaDB"
    # name = "server"
    limit = None
    a=0.2
    b=0.3
    c=0.4
    d=0.1
    
    i=0
    l=[]
    now = datetime.datetime.now()
    print "1";
    commit_history = fetch_commit_history(owner, name, limit)
    with codecs.open("{0}_{1}_commit_history.txt".format(owner, name), "w", encoding="utf8") as dst:
        for commit in commit_history:
            dst.write("{0}|{1}\n".format(commit.get('committedDate'), commit.get('url')))
    print "2"      
    for days in (30, 90, 180, 365):
        
#        print "commit number within {0}  days: ".format(days), \
        #   simple_stat(commit_history, 'committedDate', lambda x: x > now - datetime.timedelta(days=days))
        l.append(simple_stat(commit_history, 'committedDate', lambda x: x > now - datetime.timedelta(days=days)))
        
        print "day:",days,"commits:",l[i]
        i = i+1
        
    result=l[0]*a+l[1]*b+l[2]*c+l[3]*d
    print "result:",result
    
    
            


