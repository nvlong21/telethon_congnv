<template>
  <div>
    <!-- Breadcrumb -->
    <Breadcrumb breadcrumb="Forms" />

    <div class="mt-8">
      <div class="mt-4">
        <div class="p-6 bg-white rounded-md shadow-md">
          <h2 class="text-lg font-semibold text-gray-700 capitalize">
            Add task to session
          </h2>

          <form @submit.prevent="create">
            <div class="grid grid-cols-1 gap-6 mt-4 sm:grid-cols-2">
              <div>
                <label class="text-gray-700" for="phone">SDT: </label>
                <input
                  class="w-full mt-2 border-gray-200 rounded-md focus:border-indigo-600 focus:ring focus:ring-opacity-40 focus:ring-indigo-500"
                  type="text" 
                  v-model="this.phone"
                />
              </div>
            <div>
                <label>
                    <input
                    type="radio"
                    class="w-5 h-5 text-indigo-600 rounded-md focus:ring-indigo-500"
                    name="radio" value="1" v-model="task_id" @change="uniqueCheck"
                    /><span class="ml-2 text-gray-700">Crawler</span>
                </label>
                <label>
                    <input
                    type="radio"
                    class="w-5 h-5 text-indigo-600 rounded-md focus:ring-indigo-500"
                    name="radio" value="2" v-model="task_id" @change="uniqueCheck"
                    /><span class="ml-2 text-gray-700">Poster</span>
                </label>
            </div>
            <div>
                <label>
                    <span class="ml-2 text-gray-700">Danh muc: </span>
                <dropdown :options="arrayOfObjects" :selected="object" v-on:updateOption="methodToRunOnSelect"></dropdown>
                </label>
            </div>
            <!-- <vue-dropdown :config="config"></vue-dropdown> -->
              <!-- <div>
                <label class="text-gray-700" for="emailAddress"
                  >Email Address</label
                >
                <input
                  class="w-full mt-2 border-gray-200 rounded-md focus:border-indigo-600 focus:ring focus:ring-opacity-40 focus:ring-indigo-500"
                  type="email"
                  v-model="session.email"
                />
              </div> -->

              <!-- <div>
                <label class="text-gray-700" for="password">Password</label>
                <input
                  class="w-full mt-2 border-gray-200 rounded-md focus:border-indigo-600 focus:ring focus:ring-opacity-40 focus:ring-indigo-500"
                  type="password"
                  v-model="session.password"
                />
              </div> -->

              <!-- <div>
                <label class="text-gray-700" for="passwordConfirmation"
                  >Password Confirmation</label
                >
                <input
                  class="w-full mt-2 border-gray-200 rounded-md focus:border-indigo-600 focus:ring focus:ring-opacity-40 focus:ring-indigo-500"
                  type="password"
                  v-model="session.confirm"
                />
              </div>-->
            </div> 

            <div class="flex justify-end mt-4">
              <button
                class="px-4 py-2 text-gray-200 bg-gray-800 rounded-md hover:bg-gray-700 focus:outline-none focus:bg-gray-700"
              >
                Save
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script >
import { ref } from 'vue';
import Breadcrumb from '../partials/Breadcrumb.vue';
import dropdown from 'vue-dropdowns';
export default{
    components: {
        'dropdown': dropdown,
    },
    data(){
        return{
            session:{},
            notifications:[],
            phone: this.$route.params.phone,
            arrayOfObjects: [],
            task_id: 0,
            category_id: 0,
            object: {
              name: 'Object Name',
            }

        }
    },
    methods: {
        create: function()
        {
            let requestOptions = {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                "phone": this.phone,
                'task_id': this.task_id,
                'category_id': this.category_id
              })
            };
            fetch('http://localhost:8001/sessions', requestOptions)
            .then(async response => {
               let data = await response.json();
                console.log(data);
                // this.$router.push('/') 
                 this.notifications.push({
                    type: 'success',
                    message: 'Sess created successfully'
                });
            });
        },
        methodToRunOnSelect(payload) {
            console.log(payload)
        },
        getCategory(id) {
            fetch('http://localhost:8001/categories?id=' + id)
            .then(async response => {
                let datas = await response.json();
                console.log(datas);
                for(var i = 0; i < datas.length; i += 1)
                {
                    console.log();
                    this.arrayOfObjects.push({name: datas[i].name, value: datas[i].id});
                }
            });
        },
        uniqueCheck()
        {
            this.getCategory(this.task_id); 
        },

    }
    
}
</script>
