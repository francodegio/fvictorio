import collections
import os, re
import pandas as pd
import cchardet as chardet
from tqdm import tqdm


def open_file(filepath):
    with open(filepath, 'rb') as f:
        data = f.read()
        encoding = chardet.detect(data).get('encoding', None)
    with open(filepath, 'r', encoding=encoding) as f:
        data = f.read()
        
    lista = re.split(r'Página\(\d+\)', data)
    
    return [x for x in lista if 'FECHA' in x]


class Page:


    def __init__(self, page):
        self.page = page
    
    
    def _create_df(self):
        page = pd.DataFrame(self.page.split('\n'), columns=['text'])
        page['main'] = page['text'].str.contains('\d{2}\-\d+\-\d{1}')
        page['offset'] = page['text'].shift(-1)
        self.df = page


    def _find_index_title(self):
        index = self.df.loc[self.df['text'].str.contains('TIPO\sNUMERO')]
        self.index = index.index[0]
        self.title = index['text'].iloc[0]


    def _find_slices(self):
        slices = pd.DataFrame([i.span() for i in re.finditer('\|', self.title)], columns=['start', 'finish'])
        slices['shift'] = slices['start'].shift(-1)
        self.slices = slices[['finish', 'shift']].dropna().astype(int).to_numpy().tolist()


    def _parse_columns(self):
        for i, (start, finish) in enumerate(self.slices):
            self.df[f'text_{i}'] = self.df['text'].apply(lambda x: x[start:finish])
            self.df[f'offset_{i}'] = self.df['offset'].fillna('').apply(lambda x: x[start:finish])
        
        texts = ['M', 'CUIT', 'DOCUMENTO', 'NOMBRE', 'SEXO', 'I V', 'S E', 'NACIMIENTO', 'DOMICILIO', 'TELEFEONO', 'A C', 'C A', 'S I', 'CODIGO', 'USUARIO', 'FECHA']
        self.texts = dict(zip([col for col in self.df.columns if 'text_' in col], texts))
        self.offset = {'offset_8':'EMAIL', 'offset_9':'CELULAR'}
        
        self.df = self.df.rename(columns=self.texts)
        cols = [x for x in [col for col in self.df.columns if 'offset_' in col] if x not in self.offset.keys()]
        self.df = self.df.drop(columns=cols)
        self.df = self.df.rename(columns=self.offset)
        
        self.mapper = {'CALLE': (0, 31),
                  'CODIGO POSTAL': (31,35),
                  'LOCALIDAD': (37,56),
                  'PROVINCIA':  (56, -1)}
                  
        for name, (start, finish) in self.mapper.items():
            self.df[name] = self.df['DOMICILIO'].apply(lambda x: x[start:finish])

        
    def get_page_df(self):
        self._create_df()
        self._find_index_title()
        self._find_slices()
        self._parse_columns()
        cols = [x for x in self.texts.values()]\
               + [x for x in self.offset.values()]\
               + [x for x in self.mapper.keys()]

        self.result = self.df.loc[self.df['main']==True, cols]
        
        return self.result


def main(origin, destination):
    
    filenames = [os.path.join(origin, x) for x in os.listdir(origin)]
    
    for file in tqdm(filenames):
        try:
            print(file)
            data = open_file(file)
            pages = []
            try:
                for page in data:
                    result = Page(page)
                    result = result.get_page_df()
                    pages.append(result)
                    
                pages = pd.concat(pages)
                pages = pages.dropna(subset=['NOMBRE'])

                if os.path.exists(destination):
                    data = pd.read_csv(destination)
                    pages = pd.concat([data, pages], axis=0)    
                    pages = pages.drop_duplicates(subset=['CUIT'])
                    pages.to_csv(destination, mode='a', index=False, header=False)
                else:
                    pages = pages.drop_duplicates(subset=['CUIT'])
                    pages.to_csv(destination, mode='w', index=False)
            except Exception as e:
                print(e)
        except Exception as e:
            print(f"Failed to load {file}. Reason:\n{e}")

    print("Finished")