<template>
  <div class="modal-vue">
    <button @click="modalShow">Add</button>
    <div v-if="open" class="overlay" @click="modalClose"></div>
    <div v-if="open" class="modal">
      <button class="close" @click="modalClose">x</button>
      <h3>Title</h3>
      <el-form ref="form" :model="addCrawlTeleAcounts" label-width="120px">
        <el-form-item label="Crawl From">
          <el-input v-model="addCrawlTeleAcounts.list_uri" />
        </el-form-item>
        <el-form-item label="Type">
          <el-select v-model="addCrawlTeleAcounts.type" placeholder="please select category">
            <el-option label="User" value="1"  />
            <el-option label="Chanel" value="2"  />
            <el-option label="Group" value="3"  />
          </el-select>
        </el-form-item>
        </el-form-item>
        <el-form-item label="Post To">
          <el-select v-model="addCrawlTeleAcounts.category_crawl" placeholder="please select category">
            <el-option v-for="(cat, idx) in arrayCatesCrawl" :key="idx" :label="cat.name" :value="cat.value"  />
          </el-select>
        </el-form-item>
        <el-form-item label="Post To">
          <el-select v-model="addCrawlTeleAcounts.category_post" placeholder="please select category">
            <el-option v-for="(cat, idx) in arrayCatesPost" :key="idx" :label="cat.name" :value="cat.value"  />
          </el-select>
        </el-form-item>
        <el-form-item label="Filter Word">
          <el-select v-model="addCrawlTeleAcounts.category_word" placeholder="please select category">
            <el-option v-for="(cat, idx) in arrayCatesFilterWord" :key="idx" :label="cat.name" :value="cat.value"  />
          </el-select>
        </el-form-item>
        <el-form-item label="Replace Word">
          <el-select v-model="addCrawlTeleAcounts.category_replace_word" placeholder="please select category">
            <el-option v-for="(cat, idx) in arrayCatesReplaceWord" :key="idx" :label="cat.name" :value="cat.value"  />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="addCate">Create</el-button>
        </el-form-item>
      </el-form>
    </div>
    <div class="app-container">
      <el-table
        v-loading="listLoading"
        :data="crawlTeleAcounts"
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
            <span>{{ scope.row.uri }}</span>
          </template>
        </el-table-column>
        <el-table-column label="Type" align="center" width="110">
          <template slot-scope="scope">
            <span>{{ scope.row.type }}</span>
          </template>
        </el-table-column>
        <el-table-column label="Category Crawl"  align="center">
          <template slot-scope="scope">
            <span>{{ scope.row.category_crawl }}</span>
          </template>
        </el-table-column>
        <el-table-column label="Category Post"  align="center">
          <template slot-scope="scope">
            <span>{{ scope.row.category_post }}</span>
          </template>
        </el-table-column>
        <el-table-column label="Category Words"  align="center">
          <template slot-scope="scope">
            <span>{{ scope.row.category_word }}</span>
          </template>
        </el-table-column>
        <el-table-column label="Category Replace Word"  align="center">
          <template slot-scope="scope">
            <span>{{ scope.row.category_replace_word }}</span>
          </template>
        </el-table-column>
        <el-table-column label="Setting" width="110" align="center">
          <template>
            <span>Setting</span>
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
      crawlTeleAcounts: [],
      addCrawlTeleAcounts: {
        list_uri: [],
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
      object: {
        name: 'Object Name'
      }
    }
  },
  components: {
  },
  methods: {
    addCate() {
      const requestOptions = {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          'words': this.addReplaceWords.list_keyword,
          'replace': this.addReplaceWords.replace,
          'cate_id': this.addReplaceWords.cate_id
        })
      }
      fetch('http://localhost:8000/replace-words', requestOptions).then(async response => {
        this.$router.go(this.$router.currentRoute)
      })
    },
    getReplaceWorlds() {
      this.listLoading = true
      fetch('http://localhost:8000/replace-words').then(async response => {
        const datas = await response.json()
        this.replacewords = datas
        this.listLoading = false
      })
    },
    getCategory(id) {
      fetch('http://localhost:8000/categories?cate_for=filter&type_id=4').then(async response => {
        const datas = await response.json()
        for (var i = 0; i < datas.length; i += 1) {
          this.arrayCates.push({ name: datas[i].name, value: datas[i].id })
        }
        console.log(this.arrayCates)
      })
    },
    modalShow() {
      this.getCategory()
      this.open = true
    },
    modalClose() {
      this.open = false
      this.arrayCates = []
    },
    methodToRunOnSelect(payload) {
      this.addReplaceWords.cate_id = payload.value
    }
  },
  created() {
    this.getReplaceWorlds()
  }
}
</script>
