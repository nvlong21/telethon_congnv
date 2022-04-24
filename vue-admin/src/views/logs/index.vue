<template>
  <div class="app-container">
    <el-form ref="form" :model="upload_form" label-width="120px">
      <el-form-item label="Task">
        <el-select v-model="log_form.log_task" placeholder="please select log" @change="dropDownChange">
          <el-option label="Craw" value="crawl" />
          <el-option label="Post" value="post" />
          <el-option label="API" value="api" />
        </el-select>
      </el-form-item>
      <el-form-item label="File">
        <el-select v-model="log_form.log_file" placeholder="please select category">
          <el-option v-for="(cat, idx) in log_names" :key="idx" :label="cat.name" :value="cat.value" />
        </el-select>
      </el-form-item>
      <el-form-item label="From">
        <el-input v-model="log_form.from" />
      </el-form-item>
      <el-form-item label="Size">
        <el-input v-model="log_form.size" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="getLogFiles">Get</el-button>
      </el-form-item>
    </el-form>
    <el-table
      v-loading="listLoading"
      :data="log_messages"
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
      <el-table-column label="Log">
        <template slot-scope="scope">
          {{ scope.row.log_info }}
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script>
import { ref } from 'vue'
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
      listLoading: true,
      log_form: {
        log_task: null,
        log_file: null,
        from: null,
        size: null
      },
      base_app_api: process.env.VUE_APP_BASEURL,
      log_names: [],
      log_messages: []
    }
  },

  methods: {
    getLogFiles() {
      const requestOptions = {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          'log_task': this.log_form.log_task,
          'log_file': this.log_form.log_file,
          'from': this.log_form.from,
          'size': this.log_form.size
        })
      }
      fetch(this.base_app_api + '/get-log-data', requestOptions).then(async response => {
        // this.$router.go(this.$router.currentRoute)
        const data = await response.json()
        this.log_messages = data
        this.listLoading = false
      })
    },
    getLogs(id) {
      fetch(this.base_app_api + '/get-list-log?log_task=' + id).then(async response => {
        const datas = await response.json()
        
        this.log_names = []
        for (var i = 0; i < datas.length; i += 1) {
          console.log(datas[i])
          this.log_names.push({ name: datas[i], value: datas[i]})
        }
        console.log(this.log_names)
      })
    },
    dropDownChange(payload) {
      this.getLogs(payload)
    }
  }
}
</script>

