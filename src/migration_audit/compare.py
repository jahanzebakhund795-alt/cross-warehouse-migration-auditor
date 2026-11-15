from datetime import date,datetime,timezone
from decimal import Decimal
import hashlib
import json

def normalize(value):
    if value is None or isinstance(value,(str,bool)):
        return value
    if isinstance(value,(int,float,Decimal)):
        number=Decimal(str(value))
        if not number.is_finite():
            raise ValueError('Nonfinite numeric value')
        text=format(number,'f')
        if '.' in text:
            text=text.rstrip('0').rstrip('.')
        return {'$number':'0' if number.is_zero() else text}
    if isinstance(value,datetime):
        if value.tzinfo is None:
            return {'$naive_timestamp':value.isoformat()}
        return {'$timestamp':value.astimezone(timezone.utc).isoformat()}
    if isinstance(value,date):
        return {'$date':value.isoformat()}
    if isinstance(value,bytes):
        return {'$bytes':value.hex()}
    raise ValueError('Unsupported column type: '+type(value).__name__)

def canonical(row):
    return json.dumps({k:normalize(v) for k,v in row.items()},sort_keys=True,separators=(',',':'))

def audit(source,target,max_samples=20):
    left_columns,right_columns=source.validate(),target.validate()
    if set(left_columns)!=set(right_columns):
        return {'matched':False,'schema_difference':{'source':left_columns,'target':right_columns}}
    if source.key!=target.key:
        raise ValueError('Both sources must use the same key column')
    left,right=iter(source.rows()),iter(target.rows())
    a,b=next(left,None),next(right,None)
    counts={'equal':0,'changed':0,'missing':0,'extra':0}
    samples=[]
    digests=[hashlib.sha256(),hashlib.sha256()]
    def consume(row,index):
        digests[index].update((canonical(row)+'\n').encode())
    while a is not None or b is not None:
        if b is None or (a is not None and a[source.key]<b[target.key]):
            category,key='missing',a[source.key]
            consume(a,0)
            a=next(left,None)
        elif a is None or b[target.key]<a[source.key]:
            category,key='extra',b[target.key]
            consume(b,1)
            b=next(right,None)
        else:
            key=a[source.key]
            category='equal' if canonical(a)==canonical(b) else 'changed'
            consume(a,0)
            consume(b,1)
            a,b=next(left,None),next(right,None)
        counts[category]+=1
        if category!='equal' and len(samples)<max_samples:
            samples.append({'key':normalize(key),'difference':category})
    return {'matched':not any(counts[k] for k in ['changed','missing','extra']),
            'counts':counts,'samples':samples,
            'source_digest':digests[0].hexdigest(),'target_digest':digests[1].hexdigest()}
