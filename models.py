from sqlalchemy import Column, Integer, String, Text, Date
from sqlalchemy.orm.exc import NoResultFound
import db
from db import Base
import logging
import json

__all__ = ['New', 'BigDict', 'KV_util', 'kv', 'KV']


class New(Base):
    __tablename__ = 'news'
    id = Column(Integer, primary_key=True)
    raw = Column(Text)
    title = Column(String(300))
    link = Column(String(300))
    body = Column(Text(convert_unicode=True))
    clean_body = Column(Text)
    date = Column(Date)
    publisher = Column(String(300))
    source = Column(String(300))
    source_link = Column(String(300))
    search_text = Column(Text)  # combine all words together, for searching
    sha1 = Column(String(50))

    def __repr__(self):
        return '<New %s - %s>' % (self.title, self.date)

    def __unicode__(self):
        return self.__repr__()

    def to_dict(self, body=False, raw=False):
        ''' default doesn't include body of news and page raw'''
        d = {}
        keys = ['id', 'title', 'link',
                'publisher', 'source', 'source_link', 'sha1']
        if body:
            keys.append('body')
            keys.append('clean_body')
        if raw:
            keys.append('raw')
        for k in keys:
            d[k] = getattr(self, k)
        d['date'] = str(self.date)
        return d

    def to_json(self, body=False, raw=False):
        ''' default doesn't include body of news and page raw'''
        d = self.to_dict(body=body, raw=raw)
        return json.dumps(d)


class BigDict(Base):
    __tablename__ = 'bigdict'
    id = Column(Integer, primary_key=True)
    key = Column(String(200))
    val = Column(String(1000))

    def __repr__(self):
        return '<Option %s : %s>' % (self.key, self.val)

    def __unicode__(self):
        self.__repr__()

class KV_util(object):
    ''' act like a dict, using BigDict
    e.g:
    KV[1] = 123
    KV['hello'] = 'world'
    print KV.hello
    KV.hello = 'goodbye'
    print KV.nokey
    '''
    def __getattr__(self, key):
        try:
            res = BigDict.query.filter(BigDict.key == key).one()
            if res.val.isdigit():
                return int(res.val)
            else:
                return res.val
        except:
            return u''
    def __setattr__(self, key, val):
        if not isinstance(val, int):
            try:
                val = str(val)
            except:
                logging.error("store %r in BigDict failed\
                    when encode to utf-8" % val)
        try:
            q = BigDict.query.filter(BigDict.key == key)
            q.one()
            q.update({'val': val}, synchronize_session=False)
            db.ses.commit()
        except NoResultFound:
            record = BigDict(key=key, val=val)
            db.ses.add(record)
            db.ses.commit()
        except Exception, e:
            raise e

    def __getitem__(self, key):
        if isinstance(key, int):
            key = str(key)
        return getattr(self, key)

    def __setitem__(self, key, val):
        if isinstance(key, int):
            key = str(key)
        setattr(self, key, val)

KV = KV_util()
kv = KV
