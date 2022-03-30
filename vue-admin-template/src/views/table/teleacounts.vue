<template>
  <div class="modal-vue">
    <button @click="open = true">Add</button>
    <div v-if="open" class="overlay" @click="open = false"></div>
    <div v-if="open" class="modal">
      <button class="close" @click="open = false">x</button>
      <h3>Get code</h3>
      <el-form ref="form" :model="telesession" label-width="120px">
        <el-form-item label="Phone">
          <el-input v-model="telesession.phone" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="addCate">Get Code</el-button>
        </el-form-item>
      </el-form>
    </div>
    <div v-if="open_code" class="overlay" @click="open_code = true"></div>
    <div v-if="open_code" class="modal">
      <button class="close" @click="open_code = true">x</button>
      <h3>Verify code</h3>
      <el-form ref="form" :model="telesession" label-width="120px">
        <el-form-item label="Code">
          <el-input v-model="telesession.code" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="addCate">Verify</el-button>
        </el-form-item>
      </el-form>
    </div>
    <div v-if="open_add_task" class="overlay" @click="modalClose"></div>
    <div v-if="open_add_task" class="modal">
      <button class="close" @click="modalClose">x</button>
      <h3>Task</h3>
      <el-form ref="form" :model="telesession" label-width="120px">
        <el-form-item label="Task">
          <el-select v-model="telesession.task_id" @change="dropDownChange" placeholder="please select task">
            <el-option label="Crawler" value="1" />
            <el-option label="Poster" value="2" />
          </el-select>
        </el-form-item>
        <el-form-item label="Category">
          <el-select v-model="telesession.category_id" placeholder="please select category">
            <el-option v-for="(cat, idx) in arrayCates" :key="idx" :label="cat.name" :value="cat.value"  />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="addCate">Add</el-button>
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
        <el-table-column label="ID">
          <template slot-scope="scope">
            {{ scope.row.id }}
          </template>
        </el-table-column>
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
      telesession: {
        phone: null,
        code: null,
        task_id: null,
        category_id: null
      },
      open: false,
      open_code: false,
      open_add_task: false,
      arrayCates: []
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
          'phone': this.telesession.phone,
          'code': this.telesession.code,
          'task_id': this.telesession.task_id,
          'category_id': this.telesession.category_id
        })
      }
      fetch('http://localhost:8000/sessions', requestOptions).then(async response => {
        // this.$router.go(this.$router.currentRoute)
        const data = await response.json()
        console.log(data)
        if (data.status === 1) {
          if (this.telesession.phone != null) {
            if (this.telesession.code == null && this.telesession.task_id == null) {
              this.open_code = true
              this.open = false
            }
            if (this.telesession.code != null) {
              this.telesession.code = null
              this.open_code = false
              this.open_add_task = true
            }
            if (this.telesession.task_id != null) {
              this.telesession.task_id = null
            }
          }
        }
      })
    },
    fetchData() {
      this.listLoading = true
      fetch('http://localhost:8000/sessions').then(async response => {
        const datas = await response.json()
        this.list = datas
        this.listLoading = false
      })
    },
    getCategory(id) {
      fetch('http://localhost:8000/categories?cate_for=account').then(async response => {
        const datas = await response.json()
        console.log(datas)
        for (var i = 0; i < datas.length; i += 1) {
          this.arrayCates.push({ name: datas[i].name, value: datas[i].id })
        }
        console.log(this.arrayCates)
      })
    },
    modalClose() {
      this.open = false
      this.arrayCates = []
    },
    dropDownChange() {
      this.getCategory()
    }
  }
}
</script>
