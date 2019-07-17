#!/usr/bin/python3
# -*- coding: utf-8 -*-
#pip install beautifulsoup4
#pip install html5lib
from urllib.request import urlopen,urlretrieve
from urllib.error import HTTPError
from bs4 import BeautifulSoup
import os,re,json,sys

debug = False
jobClasses = [
    {
        'class':'tank',
        'name':'tank',
        'name_cn':'防护职业',
        'name_short_cn':'坦克,坦,T',
        'order':1
    },
    {
        'class':'healer',
        'name':'healer',
        'name_cn':'治疗职业',
        'name_short_cn':'奶妈,奶,H',
        'order':2,
    },
    {
        'class':'meleeDps',
        'name':'melee dps',
        'name_cn':'近战职业',
        'name_short_cn':'近战,D',
        'order':3
    },
    {
        'class':'phyRangedDps',
        'name':'physical ranged dps',
        'name_cn':'远程职业',
        'name_short_cn':'远程,远敏,D',
        'order':4
    },
    {
        'class':'magRangedDps',
        'name':'magical ranged dps',
        'name_cn':'魔法职业',
        'name_short_cn':'法师,D',
        'order':5
    }
]
jobs = [
    #healers
    {
        'job':'whitemage',
        'class':'healer',
        'weburl': 'whitemage',
        'name':'White Mage',
        'name_short':'whm',
        'name_cn':'白魔法师',
        'name_short_cn':'白魔,白',
    },
    {
        'job':'scholar',
        'class':'healer',
        'weburl': 'scholar',
        'name':'Scholar',
        'name_short':'sch',
        'name_cn':'学者',
        'name_short_cn':'学者,学',
    },
    {
        'job':'astrologian',
        'class':'healer',
        'weburl': 'astrologian',
        'name':'Astrologian',
        'name_short':'ast',
        'name_cn':'占星术师',
        'name_short_cn':'占星,占',
    },
    #tanks
    {
        'job':'paladin',
        'class':'tank',
        'weburl':'paladin',
        'name':'Paladin',
        'name_short':'pld',
        'name_cn':'骑士',
        'name_short_cn':'帕拉丁,骑',
    },
    {
        'job':'warrior',
        'class':'tank',
        'weburl':'warrior',
        'name':'Warrior',
        'name_short':'war',
        'name_cn':'战士',
        'name_short_cn':'战爹,战',
    },
    {
        'job':'darkknight',
        'class':'tank',
        'weburl':'darkknight',
        'name':'Dark Knight',
        'name_short':'drk',
        'name_cn':'暗黑骑士',
        'name_short_cn':'黑骑,暗骑',
    },
    {
        'job':'gunbreaker',
        'class':'tank',
        'weburl':'gunbreaker',
        'name':'Gun Breaker',
        'name_short':'gun',
        'name_cn':'枪刃',
        'name_short_cn':'枪',
    },
    #melee dps
    {
        'job':'monk',
        'class':'meleeDps',
        'weburl':'monk',
        'name':'Monk',
        'name_short':'mnk',
        'name_cn':'武僧',
        'name_short_cn':'秃子,僧',
    },
    {
        'job':'dragoon',
        'class':'meleeDps',
        'weburl':'dragoon',
        'name':'Dragoon',
        'name_short':'drg',
        'name_cn':'龙骑士',
        'name_short_cn':'龙骑,龙',
    },
    {
        'job':'ninja',
        'class':'meleeDps',
        'weburl':'ninja',
        'name':'Ninja',
        'name_short':'nin',
        'name_cn':'忍者',
        'name_short_cn':'忍',
    },
    {
        'job':'samurai',
        'class':'meleeDps',
        'weburl':'samurai',
        'name':'Samurai',
        'name_short':'sam',
        'name_cn':'武士',
        'name_short_cn':'侍',
    },
    # ranged
    {
        'job':'bard',
        'class':'phyRangedDps',
        'weburl':'bard',
        'name':'Bard',
        'name_short':'brd',
        'name_cn':'诗人',
        'name_short_cn':'诗',
    },
    {
        'job':'machinist',
        'class':'phyRangedDps',
        'weburl':'machinist',
        'name':'Machinist',
        'name_short':'mch',
        'name_cn':'机工士',
        'name_short_cn':'机工,机',
    },
    {
        'job':'dancer',
        'class':'phyRangedDps',
        'weburl':'dancer',
        'name':'Dancer',
        'name_short':'dan',
        'name_cn':'舞者',
        'name_short_cn':'舞',
    },
    #magic ranged
    {
        'job':'blackmage',
        'class':'magRangedDps',
        'weburl':'blackmage',
        'name':'Black Mage',
        'name_short':'blm',
        'name_cn':'黑魔法师',
        'name_short_cn':'黑魔,黑',
    },
    {
        'job':'summoner',
        'class':'magRangedDps',
        'weburl':'summoner',
        'name':'Summoner',
        'name_short':'smn',
        'name_cn':'召唤师',
        'name_short_cn':'召唤,召',
    },
    {
        'job':'redmage',
        'class':'magRangedDps',
        'weburl':'redmage',
        'name':'Red mage',
        'name_short':'rdm',
        'name_cn':'赤魔法师',
        'name_short_cn':'赤魔,赤',
    },
]

class FF14skills:

    def __init__(self):
        self.jobClasses = jobClasses
        self.jobClassesDict = {c['class']:c for c in self.jobClasses}
        self.jobs = jobs
        self.jobClassSkills= {}    # 职能技能

    def getWebpageUrl(self,placeholder):
        url = 'https://na.finalfantasyxiv.com/jobguide/{}/'.format(placeholder)
        return url

    def extractSkillTableContent(self, jobKey, tableContent, idPrefix=''):
        if debug: print('extractSkillTableContent for {} with idPrefix "{}"'.format(jobKey, idPrefix))
        skillsOfType = []
        skillsOfTypeSaved = {}
        skillTrs = tableContent.find('tbody')('tr')
        # save skills
        nextID = 0
        for skillTr in skillTrs:
            id = idPrefix
            # ignore the 'hidden' trs
            if 'class' in skillTr.attrs and 'hide' in skillTr['class']: continue
            # do not take the ID from table, but increment
            if False and 'id' in skillTr.attrs:
                id += ''.join([i for i in skillTr['id'] if i.isdigit()])
                if debug: print('handle skill with id {} from skillTr.attrs'.format(id))
            else:
                nextID += 1
                id += '{:0>2}'.format(nextID)
                if debug: print('handle skill with id {} from nextID sequence with increment.'.format(id))
            skill = {'id':id}
            for td in skillTr('td'):
                if 'class' not in td.attrs: continue    # skip TDs without class
                cls = td['class'][0]
                if cls == 'skill':          # skill name and icon
                    iconSrc = td.find('img')['src']
                    # skill['icon'] = iconSrc
                    icon = self.handleIcon(iconSrc, jobKey)
                    if icon:
                        skill['icon'] = icon.split('.')[0]  # save img name
                        # skill['img'] = iconSrc
                    skill['name'] = td.find('p').find('strong').get_text().strip("[\n\t ]")
                    if debug: print('skill name = {}'.format(skill['name']))
                elif cls in ['classification', 'cast', 'recast']:
                    skill[cls] = td.get_text().strip("[\n\t ]")
                    if debug: print('skill {} = {}'.format(cls, skill[cls]))
                elif cls == 'content':      # skill description
                    skill[cls] = [s.strip("[\n\t ]") for s in td.strings]
                elif cls == 'jobclass':     # lv when the skill could be learned
                    lv = td.find('p')
                    if lv:
                        lv = lv.get_text().lower().strip("[\n\t ]")
                        if 'lv' in lv:
                            skill['lv'] = lv.strip('lv[. ]*')
                else:
                    if debug: print('ignore td class {}'.format(cls))
                    pass
            if id in skillsOfTypeSaved:
                print('{}: skill id {} exist! {}'.format(jobKey, id, skillsOfTypeSaved[id]))
            else:
                skillsOfTypeSaved[id] = skill
            skillsOfType.append(skill)
        return skillsOfType

    def analyzeJob(self,job):
        print('-'*20, flush=True)
        jobKey = job['job']
        print('processing: '+jobKey, flush=True)
        obj = BeautifulSoup(urlopen(self.getWebpageUrl(job['weburl'])), 'html5lib')
        tempContent = obj('div', class_=['js__select--pve','job__content--battle'])
        res = {'skillTypes':[], 'job':job}
        # save Trait individually, and put to the end of skillTypes
        traits = None;
        for item in tempContent:
            skillContents = item('div', class_='job__content__wrapper')
            # get update date
            updatedAt = item.find('p', class_='job__update')
            if updatedAt:
                updatedAt = updatedAt.get_text().strip("[\n\t ]")
                search = re.search(r'([0-9\-/].*)', updatedAt)
                if search:
                    updatedAt = '/'.join(search.groups())
                res['updatedAt'] = updatedAt
                print('{} skills updated at: {}'.format(jobKey, updatedAt))
            # handle all type of skills
            skillType = ord('a') # set the number of skill type as a prefix
            for skillContent in skillContents:
                h3 = skillContent.find('h3', class_='job__sub_title')
                if h3:
                    h3Name = h3.get_text().strip("[\n\t ]")
                    if h3Name == 'Role Actions':
                        # handle 职能技能 which is not saved yet
                        jobClass = job['class']
                        if jobClass not in self.jobClassSkills:
                            jobClassSkills = self.extractSkillTableContent(jobClass, skillContent, jobClass)
                            self.jobClassSkills[jobClass] = jobClassSkills
                    elif h3Name in ['Pet Actions (Commands)']:
                        # skip: Pet Actions (commands)
                        pass
                    elif h3Name == 'Trait':
                        idPrefix = 'z'
                        # update all skills inside with passive: True
                        traits = list(map(lambda x: x.update({'passive': True}) or x, \
                                            self.extractSkillTableContent(jobKey, skillContent, idPrefix)))
                        print('{} traits processed.'.format(len(traits)));
                    else:
                        # save skill types
                        idPrefix = ''
                        if h3Name != 'Job Actions':
                            idPrefix = chr(skillType)
                            skillType += 1
                        skillsOfType = self.extractSkillTableContent(jobKey, skillContent, idPrefix)
                        res['skillTypes'].append({'name':h3Name, 'skills':skillsOfType})
                        print('{} handled with type "{}".'.format(h3Name, idPrefix))
                else:
                    # no h3 means 职业量普
                    pass
        # save traits
        if traits:
            res['skillTypes'].append({'name': 'Trait', 'skills': traits})
        return res

    def analyzeAll(self):
        res = [self.analyzeJob(j) for j in self.jobs]
        return res

    def getPath(self, type, getAbspath=False):
        cur = getAbspath and os.path.abspath(os.curdir) or os.curdir
        if type == 'skillicons':
            return os.path.join(cur, 'resources', 'skillicons')
        elif type == 'skilljs':
            return os.path.join(cur, 'resources')
        elif type == 'jobicons':
            return os.path.join(cur, 'resources', 'jobicons')
        else:
            print('Type "{}" not defined!'.format(type))
            raise Exception('error')

    def saveJobClassSkillsToFile(self):
        if len(self.jobClassSkills) == 0:
            self.analyzeAll()
        filePath = os.path.join(self.getPath('skilljs'), 'jobClassSkills.js')
        self.saveToFile(self.jobClassSkills, filePath)
        print('jobClassSkill file saved as '+filePath, flush=True)
        return self.jobClassSkills

    def saveJobSkillsToFile(self):
        skills = self.analyzeAll()
        filePath = os.path.join(self.getPath('skilljs'), 'jobSkills.js')
        self.saveToFile(skills,filePath)
        print('jobSkill file saved as '+filePath, flush=True)
        return skills

    def saveJobClassesToFile(self):
        classes = self.getJobClasses()
        filePath = os.path.join(self.getPath('skilljs'), 'jobClasses.js')
        self.saveToFile(classes, filePath)
        print('jobClasses file saved as '+filePath, flush=True)
        return classes

    def saveToFile(self, content, path, encoding='utf8'):
        with open(path, 'w', encoding=encoding) as f:
            f.write('module.exports = ');
            f.write(json.dumps(content, ensure_ascii=False))

    def getJobClasses(self):
        res = []
        for cls in self.jobClasses:
            cls['jobs'] = [job for job in self.jobs if job['class']==cls['class']]
            #cls['icon'] = '{}.png'.format(cls['class'])
            cls['icon'] = '{}'.format(cls['class'])
            res.append(cls)
        return res

    def handleIcon(self, iconUri, jobKey):
        pattern = '.*\/([a-zA-Z0-9\_\-]+)\.([a-zA-Z]+)$'
        currentPath = self.getPath('skillicons')
        if not os.path.isdir(currentPath):
            os.mkdir(currentPath)
        iconPath = os.path.join(currentPath, jobKey)
        if not os.path.isdir(iconPath):
            os.mkdir(iconPath)
        res = re.match(pattern, iconUri)
        if res:
            iconFileName = '.'.join(res.groups())
            iconFileFullPath = os.path.join(iconPath, iconFileName)
            if not os.path.isfile(iconFileFullPath):
                urlretrieve(iconUri, iconFileFullPath)
                print('{}: {} saved'.format(jobKey,iconFileName), flush=True)
            return iconFileName
        else:
            return None

if __name__ == '__main__':
    if len(sys.argv)==1:
        usage = '''
Usage:
    python ./getSkills_en.py (all/skills/classskills/classes)
        '''
        print(usage)
        sys.exit(0)
    x = FF14skills()
    for param in sys.argv:
        param = param.lower()
        if param in ['all', 'skills']:
            x.saveJobSkillsToFile()
        if param in ['all', 'classskills']:
            x.saveJobClassSkillsToFile()
        if param in ['all', 'classes']:
            x.saveJobClassesToFile()
        if param == 'debug':
            print('enable debug')
            debug = True
        matchedJob = next(filter(lambda x: param in x.values(), jobs), False)
        if matchedJob:
            print('analyze job {}'.format(matchedJob['job']))
            x.analyzeJob(matchedJob)

    #x.saveJobSkillsToFile()
    #x.saveJobClassSkillsToFile()
    #x.saveJobClassesToFile()
    #print(x.getJobClasse())
