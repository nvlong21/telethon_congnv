<template>
  <div>
    <!-- Breadcrumb -->
    <Breadcrumb breadcrumb="Forms" />
    <div class="mt-8">
      <h4 class="text-gray-600">Forms</h4>
      <div class="mt-4">
        <div class="p-6 bg-white rounded-md shadow-md">
          <h2 class="text-lg font-semibold text-gray-700 capitalize">
            Vertify Code
          </h2>

          <form @submit.prevent="verify">
            <div class="grid grid-cols-1 gap-6 mt-4 sm:grid-cols-2">
              <div>
                <label class="text-gray-700" for="phone">Code: </label>
                <input
                  class="w-full mt-2 border-gray-200 rounded-md focus:border-indigo-600 focus:ring focus:ring-opacity-40 focus:ring-indigo-500"
                  type="text"
                  v-model="session.code"
                />
              </div>

            </div> 

            <div class="flex justify-end mt-4">
              <button
                class="px-4 py-2 text-gray-200 bg-gray-800 rounded-md hover:bg-gray-700 focus:outline-none focus:bg-gray-700"
              >
                Verify
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

export default{
    data(){
        return{
            session:{},
            notifications:[],
            phone: this.$route.params.phone,
        }
    },
    methods: {
        verify: function()
        {
            const requestOptions = {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                "phone": this.phone,
                'code': this.session.code
              })
            };
            fetch('http://localhost:8001/verify-code', requestOptions)
            .then(async response => {
               const data = await response.json();
                console.log(data);
                this.$router.push({name: 'CreateTask', params: {"phone": this.phone}});
                 this.notifications.push({
                    type: 'success',
                    message: 'Sess created successfully'
                });
            });
        }
    }
}

</script>
