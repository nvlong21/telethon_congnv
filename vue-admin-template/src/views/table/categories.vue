<template>
  <div class="modal-vue">
    <button @click="open = true">Add</button>
    <div v-if="open" class="overlay" @click="open = false"></div>
    <div v-if="open" class="modal">
      <button class="close" @click="open = false">x</button>
      <h3>Title</h3>
      <el-form ref="form" :model="category" label-width="120px">
        <el-form-item label="Activity name">
          <el-input v-model="category.name" />
        </el-form-item>
        <el-form-item label="Activity zone">
          <el-select v-model="category.task_id" placeholder="please select your zone">
            <el-option label="Craw" value="1" />
            <el-option label="Post" value="2" />
            <el-option label="Key Words" value="3" />
            <el-option label="Words Replace" value="4" />
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
        :data="list"
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
        <el-table-column label="Name">
          <template slot-scope="scope">
            {{ scope.row.name }}
          </template>
        </el-table-column>
        <el-table-column label="Type" width="110" align="center">
          <template slot-scope="scope">
            <span>{{ scope.row.type }}</span>
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
  filters: {
    statusFilter(status) {
      const statusMap = {
        published: 'success',
        draft: 'gray',
        deleted: 'danger'
      }
      return statusMap[status]
    }
  },
  data() {
    return {
      list: null,
      listLoading: true,
      categories: [],
      category: {
        name: null,
        task_id: 0
      },
      open: false
    }
  },
  created() {
    this.fetchData()
  },
  methods: {
    addCate() {
      const requestOptions = {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          'name': this.category.name,
          'type_id': this.category.task_id
        })
      }
      fetch('http://localhost:8000/categories', requestOptions).then(async response => {
        this.$router.go(this.$router.currentRoute)
        console.log(response)
      })
    },
    fetchData() {
      this.listLoading = true
      fetch('http://localhost:8000/categories').then(async response => {
        const datas = await response.json()
        this.list = datas
        this.listLoading = false
      })
    },
    uniqueCheck() {
      console.log('a')
    }
  }
}
</script>
