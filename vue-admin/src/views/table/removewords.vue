<template>
  <div class="modal-vue">
    <div v-if="open" class="overlay" @click="modelClose"></div>
    <div v-if="open" class="modal">
      <button class="close" @click="open = false">x</button>
      <h3>Stop Words Add</h3>
      <el-form ref="form" :model="addRemoveWords" label-width="120px">
        <el-form-item label="Category">
          <el-select v-model="addRemoveWords.cate_id" placeholder="please select category">
            <el-option v-for="(cat, idx) in arrayCates" :key="idx" :label="cat.name" :value="cat.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="Words">
          <el-input v-model="addRemoveWords.list_removeword" type="textarea" />
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
        :data="remove_words"
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
        <el-table-column label="Stop Word" align="center">
          <template slot-scope="scope">
            <span>{{ scope.row.stop_word }}</span>
          </template>
        </el-table-column>
        <el-table-column label="Category" width="150" align="center">
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
      remove_words: [],
      addRemoveWords: {
        list_removeword: [],
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
  components: {
  },
  methods: {
    addCate() {
      const requestOptions = {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          'remove_words': this.addRemoveWords.list_removeword,
          'cate_id': this.addRemoveWords.cate_id
        })
      }
      fetch(this.base_app_api + '/remove-words', requestOptions).then(async response => {
        fetch(this.base_app_api + '/reload-db').then(async response => {
          
        })
        const datas = await response.json()
        alert(datas.message)
        this.$router.go(this.$router.currentRoute)
      })
    },
    getRemoveWorlds() {
      this.listLoading = true
      fetch(this.base_app_api + '/remove-words').then(async response => {
        const datas = await response.json()
        this.remove_words = datas
        this.listLoading = false
      })
    },
    getCategory(id) {
      fetch(this.base_app_api + '/categories?type_id=5').then(async response => {
        const datas = await response.json()
        for (var i = 0; i < datas.length; i += 1) {
          this.arrayCates.push({ name: datas[i].name, value: datas[i].id })
          console.log(datas[i].id)
        }
      })
    },
    deleteByID(id) {
      fetch(this.base_app_api + '/remove-word/' + id, { method: 'DELETE' }).then(async response => {
        fetch(this.base_app_api + '/reload-db').then(async response => {
          
        })
        const datas = await response.json()
        alert(datas.message)
        this.$router.go(this.$router.currentRoute)
      })
    },
    modalShow() {
      this.getCategory()
      this.open = true
    },
    modelClose() {
      this.open = false
      this.arrayCates = []
    },
    methodToRunOnSelect(payload) {
      this.addRemoveWords.cate_id = payload.value
    }
  },
  created() {
    this.getRemoveWorlds()
  }
}
</script>
