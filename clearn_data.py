from openai import OpenAI
from zhipuai import ZhipuAI
from dotenv import load_dotenv
load_dotenv()
def img2text_response( img_path: str )->map:
    with open(img_path, 'rb') as img_file:
        img_base = base64.b64encode(img_file.read()).decode('utf-8')
    client = ZhipuAI(api_key=os.environ.get("ZHIPUAI_API_KEY"))
    response = client.chat.completions.create(
        model="glm-4v-flash",  # 填写需要调用的模型名称
        messages=[
          {
            "role": "user",
            "content": [
              {
                "type": "image_url",
                "image_url": {
                    "url": img_base
                }
              },
              {
                "type": "text",
                "text": "提取图片文字，描述一下图片内容，返回json数据 { text: 图片文字(没有为None) , description: 图片内容描述 }"
              }
            ]
          }
        ],
        response_format={
        'type': 'json_object'
    }
    )
    return response.choices[0].message.content


def img2text(content:str)->str:
    string = copy( content) 
    while string.find("![]") != -1 :
        start = string.find("![]") 
        end = string.find( ")" , start) 
        path = os.path.join("output",string[start+len("![]("):end])
        img_response=  img2text_response( path ) + "\n备注 text:为图片中的文字 ,description:图片中的内容描述"
        string = string.replace( string[start :end+1],img_response)
    return string 

def HTML2index(content:str)->list:
    dx = []
    index_now = 0 
    while content.find( "<html>" , index_now )  != -1 :
        start = content.find( "<html>" , index_now ) 
        end = content.find("</html>" ,index_now ) 
        index_now = end + len("</html>") +1 
        dx.append( (start ,end + len("</html>") ) )
    flag = [False]*len(dx)
    ddx =[]
    
    for i in range( len( dx ) ) :
        if flag[i] == False:
            flag[i] = True
            start = dx[i][0]
            end = dx[i][1]
            ii = i + 1
            while ii < len( dx):
                if ( dx[ii][0] - end ) <= 3:
                    end = dx[ii][1]
                    flag[ii] = True
                else :
                    break 
                ii += 1 
            ddx.append( (start ,end) )
    return ddx 