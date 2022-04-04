<template>
  <div class="modal-vue">
    <div v-if="open" class="overlay" @click="modalClose"></div>
    <div v-if="open" class="modal">
      <button class="close" @click="modalClose">x</button>
      <h3>Title</h3>
      <el-form ref="form" :model="addReplaceWords" label-width="120px">
        <el-form-item label="Category">
          <el-select v-model="addReplaceWords.cate_id" placeholder="please select category">
            <el-option v-for="(cat, idx) in arrayCates" :key="idx" :label="cat.name" :value="cat.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="Word">
          <el-input v-model="addReplaceWords.list_keyword" type="textarea" />
        </el-form-item>
        <el-form-item label="Replace">
          <el-input v-model="addReplaceWords.replace" type="textarea" />
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
        :data="replacewords"
        element-loading-text="Loading"
        border
        fit
        highlight-current-row
      >
        <el-table-column align="center" label="ID" width="95">
          <template slot-scope="scope">
            {{ scope.$index }}
          </template>
        </el-table-column>
        <el-table-column label="Keyword" align="center">
          <template slot-scope="scope">
            <span>{{ scope.row.word }}</span>
          </template>
        </el-table-column>
        <el-table-column label="Replace" align="center">
          <template slot-scope="scope">
            <span>{{ scope.row.replace }}</span>
          </template>
        </el-table-column>
        <el-table-column label="Category" width="110" align="center">
          <template slot-scope="scope">
            <span>{{ scope.row.category }}</span>
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
      replacewords: [],
      addReplaceWords: {
        list_keyword: [],
        replace: '',
        cate_id: ''
      },
      listLoading: false,
      arrayCates: [],
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
          'words': this.addReplaceWords.list_keyword,
          'replace': this.addReplaceWords.replace,
          'cate_id': this.addReplaceWords.cate_id
        })
      }
      fetch(this.base_app_api + '/replace-words', requestOptions).then(async response => {
        this.$router.go(this.$router.currentRoute)
      })
    },
    getReplaceWorlds() {
      this.listLoading = true
      fetch(this.base_app_api + '/replace-words').then(async response => {
        const datas = await response.json()
        this.replacewords = datas
        this.listLoading = false
      })
    },
    deleteByID(id) {
      fetch(this.base_app_api + '/replace-word/' + id, { method: 'DELETE' }).then(async response => {
        console.log(response)
        this.$router.go(this.$router.currentRoute)
      })
    },
    getCategory(id) {
      fetch(this.base_app_api + '/categories?type_id=4').then(async response => {
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
