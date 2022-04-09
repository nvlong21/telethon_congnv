<template>
  <div class="modal-vue">
    <div v-if="open" class="overlay" @click="modalClose"></div>
    <div v-if="open" class="modal">
      <button class="close" @click="modalClose">x</button>
      <h3>Title</h3>
      <el-form ref="form" :model="addCrawlProcess" label-width="120px">
        <el-form-item label="Crawl From">
          <el-input v-model="addCrawlProcess.list_from" type="textarea" />
        </el-form-item>
        <el-form-item label="Type">
          <el-select v-model="addCrawlProcess.type" placeholder="please select category">
            <el-option label="User" value="1" />
            <el-option label="Chanel" value="2" />
            <el-option label="Group" value="3" />
          </el-select>
        </el-form-item>
        <el-form-item label="Category Crawl">
          <el-select v-model="addCrawlProcess.category_crawl" placeholder="please select category">
            <el-option v-for="(cat, idx) in arrayCatesCrawl" :key="idx" :label="cat.name" :value="cat.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="Post To">
          <el-select v-model="addCrawlProcess.category_post" placeholder="please select category">
            <el-option v-for="(cat, idx) in arrayCatesPost" :key="idx" :label="cat.name" :value="cat.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="Filter Word">
          <el-select v-model="addCrawlProcess.category_word" placeholder="please select category">
            <el-option v-for="(cat, idx) in arrayCatesFilterWord" :key="idx" :label="cat.name" :value="cat.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="Stop Word">
          <el-select v-model="addCrawlProcess.category_stopword" placeholder="please select category">
            <el-option v-for="(cat, idx) in arrayCatesStopWord" :key="idx" :label="cat.name" :value="cat.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="Replace Word">
          <el-select v-model="addCrawlProcess.category_replace_word" placeholder="please select category">
            <el-option v-for="(cat, idx) in arrayCatesReplaceWord" :key="idx" :label="cat.name" :value="cat.value" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="addCate">Create</el-button>
        </el-form-item>
      </el-form>
    </div>
    <div class="app-container">
      <el-button type="primary" @click="modalShow">Add</el-button>
      <el-table
        v-loading="listLoading"
        :data="crawlProcess"
        element-loading-text="Loading"
        border
        fit
        highlight-current-row
      >
        <el-table-column label="ID" width="150">
          <template slot-scope="scope">
            {{ scope.row.id }}
          </template>
        </el-table-column>
        <el-table-column label="Crawl From" width="280">
          <template slot-scope="scope">
            <span>{{ scope.row.from }}</span>
          </template>
        </el-table-column>
        <el-table-column label="Type" align="center" width="110">
          <template slot-scope="scope">
            <span>{{ scope.row.type }}</span>
          </template>
        </el-table-column>
        <el-table-column label="Category Crawl" align="center">
          <template slot-scope="scope">
            <a @click="changeCatid(scope.row.category_crawl_id)"><span>{{ scope.row.category_crawl }}</span></a>
          </template>
        </el-table-column>
        <el-table-column label="Category Post" align="center">
          <template slot-scope="scope">
            <router-link :to="{ name: 'PostProcess', params: { cate_id:  scope.row.category_post_id}}" ><span>{{ scope.row.category_post }}</span></router-link>
          </template>
        </el-table-column>
        <el-table-column label="Category Words" align="center">
          <template slot-scope="scope">
            <router-link :to="{ name: 'KeyWords', params: { cate_id:  scope.row.category_word_id}}" ><span>{{ scope.row.category_word }}</span></router-link>
          </template>
        </el-table-column>
        <el-table-column label="Category Stop Words" align="center">
          <template slot-scope="scope">
            <router-link :to="{ name: 'RemoveWords', params: { cate_id:  scope.row.category_stopword_id}}" ><span>{{ scope.row.category_stopword }}</span></router-link>
          </template>
        </el-table-column>
        <el-table-column label="Category Replace Word" align="center">
          <template slot-scope="scope">
            <router-link :to="{ name: 'ReplaceWords', params: { cate_id:  scope.row.category_replace_word_id}}" ><span>{{ scope.row.category_replace_word }}</span></router-link>
          </template>
        </el-table-column>
        <el-table-column label="Setting" width="110" align="center">
          <template slot-scope="scope">
            <el-button style="padding: 2px 5px;" type="danger" @click="deleteByID(scope.row.id)">Delete</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      cate_id: this.$route.params.cate_id,
      crawlProcess: [],
      addCrawlProcess: {
        list_from: [],
        type: '',
        category_crawl: '',
        category_post: '',
        category_word: '',
        category_replace_word: '',
        category_stopword:''
      },
      listLoading: false,
      arrayCatesReplaceWord: [],
      arrayCatesPost: [],
      arrayCatesCrawl: [],
      arrayCatesFilterWord: [],
      arrayCatesStopWord: [],
      open: false,
      base_app_api: process.env.VUE_APP_BASEURL,
      object: {
        name: 'Object Name'
      }
    }
  },
  methods: {
    addCate() {
      const requestOptions = {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          'froms': this.addCrawlProcess.list_from,
          'type': this.addCrawlProcess.type,
          'cate_id': this.addCrawlProcess.category_crawl,
          'category_keyword_id': this.addCrawlProcess.category_word,
          'category_post_id': this.addCrawlProcess.category_post,
          'category_replace_id': this.addCrawlProcess.category_replace_word
        })
      }
      fetch(this.base_app_api + '/craw-process', requestOptions).then(async response => {
        fetch(this.base_app_api + '/reload-db').then(async response => {
          const datas = await response.json()
          console.log(datas)
        })
        this.$router.go(this.$router.currentRoute)
      })
    },
    getCrawlData() {
      this.listLoading = true
      let sub_url = '/craw-process'
      if (!!this.cate_id) {
        sub_url = sub_url + '?cat_id=' + this.cate_id
      }
      fetch(this.base_app_api + sub_url).then(async response => {
        const datas = await response.json()
        this.crawlProcess = datas
        this.listLoading = false
      })
    },
    getCategory(id) {
      fetch('http://localhost:8001/categories?type_id=1').then(async response => {
        const datas = await response.json()
        for (var i = 0; i < datas.length; i += 1) {
          this.arrayCatesCrawl.push({ name: datas[i].name, value: datas[i].id })
        }
        console.log(this.arrayCatesCrawl)
      })
      fetch(this.base_app_api + '/categories?type_id=2').then(async response => {
        const datas = await response.json()
        for (var i = 0; i < datas.length; i += 1) {
          this.arrayCatesPost.push({ name: datas[i].name, value: datas[i].id })
        }
        console.log(this.arrayCatesPost)
      })
      fetch(this.base_app_api + '/categories?type_id=3').then(async response => {
        const datas = await response.json()
        for (var i = 0; i < datas.length; i += 1) {
          this.arrayCatesFilterWord.push({ name: datas[i].name, value: datas[i].id })
        }
        console.log(this.arrayCatesFilterWord)
      })
      fetch(this.base_app_api + '/categories?type_id=4').then(async response => {
        const datas = await response.json()
        for (var i = 0; i < datas.length; i += 1) {
          this.arrayCatesReplaceWord.push({ name: datas[i].name, value: datas[i].id })
        }
        console.log(this.arrayCatesReplaceWord)
      })
      fetch(this.base_app_api + '/categories?type_id=5').then(async response => {
        const datas = await response.json()
        for (var i = 0; i < datas.length; i += 1) {
          this.arrayCatesStopWord.push({ name: datas[i].name, value: datas[i].id })
        }
        console.log(this.arrayCatesReplaceWord)
      })
    },
    deleteByID(id) {
      fetch(this.base_app_api + '/craw-process/' + id, { method: 'DELETE' }).then(async response => {
        
        this.$router.go(this.$router.currentRoute)
      })
    },
    modalShow() {
      this.getCategory()
      this.open = true
    },
    changeCatid(id) {
      this.listLoading = true
      let sub_url = '/craw-process'
      if (!!id) {
        sub_url = sub_url + '?cat_id=' + id
      }
      fetch(this.base_app_api + sub_url).then(async response => {
        const datas = await response.json()
        this.crawlProcess = datas
        this.listLoading = false
      })
    },
    modalClose() {
      this.open = false
      this.arrayCatesCrawl = []
      this.arrayCatesPost = []
      this.arrayCatesFilterWord = []
      this.arrayCatesReplaceWord = []
    },
    methodToRunOnSelect(payload) {
      this.addReplaceWords.cate_id = payload.value
    }
  },
  created() {
    this.getCrawlData()
  }
}
</script>
