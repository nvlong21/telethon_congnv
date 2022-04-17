<template>
  <div class="modal-vue">
    <div v-if="open" class="overlay" @click="modalClose"></div>
    <div v-if="open" class="modal">
      <button class="close" @click="modalClose">x</button>
      <h3>Title</h3>
      <el-form ref="form" :model="addCrawlProcess" label-width="120px">
        <el-form-item label="Post To">
          <el-input v-model="addCrawlProcess.list_from" type="textarea" />
        </el-form-item>
        <el-form-item label="Type">
          <el-select v-model="addCrawlProcess.type" placeholder="please select category">
            <el-option label="User" value="1" />
            <el-option label="Chanel" value="2" />
            <el-option label="Group" value="3" />
          </el-select>
        </el-form-item>

        <el-form-item label="Post To">
          <el-select v-model="addCrawlProcess.category_post" placeholder="please select category">
            <el-option v-for="(cat, idx) in arrayCatesPost" :key="idx" :label="cat.name" :value="cat.value" />
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
        <el-table-column label="Post To" width="280">
          <template slot-scope="scope">
            <span>{{ scope.row.post_to }}</span>
          </template>
        </el-table-column>
        <el-table-column label="Type" align="center" width="110">
          <template slot-scope="scope">
            <span>{{ scope.row.type }}</span>
          </template>
        </el-table-column>
        <el-table-column label="Category Post" align="center">
          <template slot-scope="scope">
            <router-link :to="{ name: 'Category', params: { cate_id:  scope.row.category_post_id }}" ><span>{{ scope.row.category_post }}</span></router-link>
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
        category_replace_word: ''
      },
      listLoading: false,
      arrayCatesReplaceWord: [],
      arrayCatesPost: [],
      arrayCatesCrawl: [],
      arrayCatesFilterWord: [],
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
          'posts_to': this.addCrawlProcess.list_from,
          'type': this.addCrawlProcess.type,
          'category_post': this.addCrawlProcess.category_crawl
        })
      }
      fetch(this.base_app_api + '/post-process', requestOptions).then(async response => {
        fetch(this.base_app_api + '/reload-db').then(async response => {
          const datas = await response.json()
          console.log(datas)
        })
        this.$router.go(this.$router.currentRoute)
      })
    },
    getPostData() {
      this.listLoading = true
      let sub_url = '/post-process'
      console.log(this.cate_id)
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
    },
    deleteByID(id) {
      fetch(this.base_app_api + '/post-process/' + id, { method: 'DELETE' }).then(async response => {
        fetch(this.base_app_api + '/reload-db').then(async response => {
          const datas = await response.json()
          console.log(datas)
        })
        this.$router.go(this.$router.currentRoute)
      })
    },
    modalShow() {
      this.getCategory()
      this.open = true
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
    this.getPostData()
  }
}
</script>
