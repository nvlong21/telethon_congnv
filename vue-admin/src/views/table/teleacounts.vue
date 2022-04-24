<template>
  <div class="modal-vue">
    <div v-if="open_upload" class="overlay" @click="open_upload = true"> </div>
    <div v-if="open_upload" class="modal">
      <button class="close" @click="open_upload = false">x</button>
      <h3>Upload session</h3>
      <el-form ref="form" :model="upload_form" label-width="120px">
        <el-form-item label="Session">
          <input type="file"  @change="handleFileUpload( $event )"/>
        </el-form-item>
        <el-form-item label="Task">
          <el-select v-model="upload_form.task_id" placeholder="please select task" @change="dropDownTaskChange">
            <el-option label="Crawler" value="1" />
            <el-option label="Poster" value="2" />
          </el-select>
        </el-form-item>
        <el-form-item label="Category">
          <el-select v-model="upload_form.category_id" placeholder="please select category">
            <el-option v-for="(cat, idx) in arrayCates" :key="idx" :label="cat.name" :value="cat.value" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="Upload">Upload</el-button>
        </el-form-item>
      </el-form>
    </div>
    <div v-if="open" class="overlay" @click="open = false"> </div>
    <div v-if="open" class="modal">
      <button class="close" @click="open = false">x</button>
      <h3>Get code</h3>
      <el-form ref="form" :model="telesession" label-width="120px">
        <el-form-item label="Phone">
          <el-input v-model="telesession.phone" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="addAccount">Get Code</el-button>
        </el-form-item>
      </el-form>
    </div>
    <div v-if="open_code" class="overlay" @click="open_code = true"> </div>
    <div v-if="open_code" class="modal">
      <button class="close" @click="open_code = true">x</button>
      <h3>Verify code</h3>
      <el-form ref="form" :model="telesession" label-width="120px">
        <el-form-item label="Code">
          <el-input v-model="telesession.code" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="addAccountCode">Verify</el-button>
        </el-form-item>
      </el-form>
    </div>
    <div v-if="open_add_task" class="overlay" @click="modalClose"> </div>
    <div v-if="open_add_task" class="modal">
      <button class="close" @click="modalClose">x</button>
      <h3>Task</h3>
      <el-form ref="form" :model="telesession" label-width="120px">
        <el-form-item label="Task">
          <el-select v-model="telesession.task_id" placeholder="please select task" @change="dropDownTaskChange">
            <el-option label="Crawler" value="1" />
            <el-option label="Poster" value="2" />
          </el-select>
        </el-form-item>
        <el-form-item label="Category">
          <el-select v-model="telesession.category_id" placeholder="please select category">
            <el-option v-for="(cat, idx) in arrayCates" :key="idx" :label="cat.name" :value="cat.value" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="addAccountTask">Add</el-button>
        </el-form-item>

      </el-form>
    </div>
    <div class="app-container">
      <el-button type="primary" @click="open = true">Add</el-button>
      <el-button type="primary" @click="open_upload = true">Upload Session</el-button>
      <el-table
        v-loading="listLoading"
        :data="list"
        element-loading-text="Loading"
        border
        fit
        highlight-current-row
      >
        <el-table-column label="Name">
          <template slot-scope="scope">
            {{ scope.row.phone }}
          </template>
        </el-table-column>
        <el-table-column label="Task" width="110" align="center">
          <template slot-scope="scope">
            <span>{{ scope.row.task }}</span>
          </template>
        </el-table-column>
        <el-table-column label="Category" width="110" align="center">
          <template slot-scope="scope">
            <span>{{ scope.row.category }}</span>
          </template>
        </el-table-column>
        <el-table-column label="Status" width="110" align="center">
          <template slot-scope="scope">
            <span>{{ scope.row.status }}</span>
          </template>
        </el-table-column>
        <el-table-column label="Setting" width="110" align="center">
          <template slot-scope="scope">
            <el-button style="padding: 2px 5px;" type="danger" @click="deleteByID(scope.row.phone)">Delete</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
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
      upload_form:{
        file: null,
        task_id: null,
        category_id: null
      },
      list: null,
      listLoading: true,
      telesession: {
        phone: null,
        code: null,
        task_id: null,
        category_id: null
      },
      open: false,
      open_upload: false,
      base_app_api: process.env.VUE_APP_BASEURL,
      open_code: false,
      open_add_task: false,
      arrayCates: []
    }
  },
  created() {
    this.fetchData()
  },
  methods: {
    handleFileUpload( event ){
      this.upload_form.file = event.target.files[0]
      console.log(this.upload_form.file)
    },
    Upload() {
      const formData = new FormData();
      formData.append('file', this.upload_form.file);
      formData.append('task_id',  this.upload_form.task_id);
      formData.append('category_id', this.upload_form.category_id);
      const requestData = {
        method: 'POST',
        // headers: { 'Content-Type': 'multipart/form-data' },
        body: formData
      }
      fetch(this.base_app_api + '/sessions-upload', requestData).then(async response => {
        console.log(await response.json())
      })

    },
    addAccountCode() {
      const requestOptions = {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          'phone': this.telesession.phone,
          'code': this.telesession.code
        })
      }
      fetch(this.base_app_api + '/sessions-code', requestOptions).then(async response => {
        // this.$router.go(this.$router.currentRoute)
        const data = await response.json()
        if (data.status === 1) {
          if (this.telesession.phone != null) {
            if (this.telesession.code != null) {
              this.telesession.code = null
              this.open_code = false
              this.open_add_task = true
            }
          }
        } else if (data.status === 2) {
          this.open = false
          this.open_code = false
          this.open_add_task = true
        }
        else{
          alert(datas.message)
        }
      })
    },
    addAccountTask() {
      const requestOptions = {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          'phone': this.telesession.phone,
          'task_id': this.telesession.task_id,
          'category_id': this.telesession.category_id
        })
      }
      fetch(this.base_app_api + '/sessions-task', requestOptions).then(async response => {
        // this.$router.go(this.$router.currentRoute)
        const data = await response.json()
        if (data.status === 1) {
          if (this.telesession.phone != null) {
            if (this.telesession.task_id != null) {
              this.telesession.task_id = null
              this.open_add_task = false
              fetch(this.base_app_api + '/reload-db').then(async response => {
              })
              this.$router.go(this.$router.currentRoute)
            }
          }
        } else {
          alert(datas.message)
        }
      })
    },
    addAccount() {
      const requestOptions = {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          'phone': this.telesession.phone
        })
      }
      fetch(this.base_app_api + '/sessions', requestOptions).then(async response => {
        // this.$router.go(this.$router.currentRoute)
        const data = await response.json()
        if (data.status === 1) {
          if (this.telesession.phone != null) {
            this.open_code = true
            this.open = false
            this.open_add_task = false
          }
        } else if (data.status === 2) {
          this.open = false
          this.open_code = false
          this.open_add_task = true
        }
        else{
          alert(data.message)
        }
      })
    },
    deleteByID(id) {
      fetch(this.base_app_api + '/session/' + id, { method: 'DELETE' }).then(async response => {
        fetch(this.base_app_api + '/reload-db').then(async response => {
          console.log(response)
        })
        const datas = await response.json()
        alert(datas.message)
        this.$router.go(this.$router.currentRoute)
      })
    },
    fetchData() {
      this.listLoading = true
      fetch(this.base_app_api + '/sessions').then(async response => {
        const datas = await response.json()
        this.list = datas
        this.listLoading = false
      })
    },
    getCategory(id) {
      fetch(this.base_app_api + '/categories?type_id=' + id).then(async response => {
        const datas = await response.json()
        this.arrayCates = []
        for (var i = 0; i < datas.length; i += 1) {
          this.arrayCates.push({ name: datas[i].name, value: datas[i].id })
        }
        console.log(this.arrayCates)
      })
    },
    modalClose() {
      this.open_add_task = false
      this.arrayCates = []
    },
    dropDownTaskChange(payload) {
      console.log(payload)
      this.getCategory(payload)
    }
  }
}
</script>
